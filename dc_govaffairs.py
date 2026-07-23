"""
dc_govaffairs.py — in-house government-affairs capability flag per prospect.

Question answered per company: does it run its own India public-policy / government-
affairs function? If yes, TAG's gov-affairs wedge is weaker (harder to win) — surfaced
as an advisory BADGE with a clickable evidence source. Never a gate: companies still
rank normally (per the BD decision), the badge only informs winnability.

Grounded, layered, cheapest-first. Nemotron has NO internet, so the LLM only ever
CLASSIFIES TEXT WE FETCH — world-knowledge guessing is never used:
  1. curated  — HAS_INHOUSE_GOVAFFAIRS (Workday giants whose ATS we can't scrape)
  2. jobs     — SS4 job-posting rows whose title is a gov-affairs/policy role (LLM-judged)
  3. news     — SS1/SS2 headlines naming a company's policy/gov-affairs leadership (LLM)
  4. web      — Firecrawl search snippets for still-unknown prospects (opt-in, FIRECRAWL_API_KEY)

Cache (govaffairs_cache.json) — never re-searches from scratch:
  - items    : {item_key: bool}  — a scraped posting/headline is LLM-judged ONCE, ever
  - companies: {company_lc: {flag, source, evidence_url, evidence, first_seen}} — sticky

Non-fatal everywhere: no key / connection fail -> falls back to whatever earlier layers
found (curated always works offline). The pipeline never breaks on this module.
"""
import json
import os
import urllib.request
from datetime import date

import dc_config as dc

CACHE_PATH = os.path.join(os.path.dirname(__file__), "govaffairs_cache.json")
WEB_LOOKUP_MAX = 8            # per-run cap on Firecrawl searches
WEB_LOOKUP_MONTHLY_MAX = 200  # hard monthly credit guard (Firecrawl free tier = 1000 credits/mo)
# ponytail: once-ever-per-company cache means lifetime web usage ~= watchlist size; these caps
# are pure insurance so a promote-storm can never blow the budget.


# --- cache -----------------------------------------------------------------
def load_cache():
    if os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH, encoding="utf-8") as f:
                c = json.load(f)
                c.setdefault("items", {})
                c.setdefault("companies", {})
                c.setdefault("usage", {})
                return c
        except Exception:
            pass
    return {"items": {}, "companies": {}, "usage": {}}


def save_cache(c):
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(c, f, ensure_ascii=False, separators=(",", ":"))


# --- helpers ---------------------------------------------------------------
def _norm(s):
    return (s or "").strip().lower()


def _is_govaffairs_role(text):
    """Cheap keyword pre-gate — only plausible rows reach the LLM (keeps the batch clean;
    a 'Data Centre Engineer' posting never gets asked about)."""
    t = _norm(text)
    return any(term in t for term in dc.GOVAFFAIRS_ROLE_TERMS)


def _match_company(actor, companies_lc):
    """Job actor is often an ATS slug ('airtrunk'); news actor a display name. Match either
    direction, case-insensitive substring — same loose rule the gazetteer/_mentions use."""
    a = _norm(actor)
    if not a:
        return None
    for co_lc, co in companies_lc.items():
        if co_lc in a or a in co_lc:
            return co
    return None


_SYSTEM = (
    "detailed thinking off\n\n"
    "You decide, from ONLY the snippet given, whether it is evidence that a company runs its "
    "OWN in-house government-affairs / public-policy / regulatory-affairs function (e.g. a job "
    "posting for such a role at the company, or news naming the company's policy/government-"
    "affairs leadership). A generic mention of 'policy' or a government BODY is NOT evidence. "
    "Use ONLY the text; do NOT use outside knowledge; if unclear, gov=false.\n\n"
    "Output ONLY a JSON array, one object per input, no prose:\n"
    '[{"key":"<key>","gov":true}]'
)


def _llm_classify(items):
    """items: [{'key','company','kind','text'}] -> {key: bool}. Grounded, one batched call,
    id-validated (hallucinated keys dropped). {} on no-key / fail (caller keeps earlier layers)."""
    if not items:
        return {}
    import dc_ai
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        return {}
    ok, note, _ = dc_ai.test_connection(key)
    if not ok:
        print(f"  [govaffairs-ai] skipped ({note})")
        return {}
    user = "Classify each snippet:\n" + "\n".join(
        json.dumps({"key": it["key"], "company": it["company"],
                    "kind": it["kind"], "text": it["text"][:400]}, ensure_ascii=False)
        for it in items)
    try:
        raw = dc_ai._chat(key, _SYSTEM, user, max_tokens=1200, temperature=0.0)
        arr = dc_ai._json_array(raw)
        want = {it["key"] for it in items}
        return {str(o["key"]): bool(o.get("gov"))
                for o in arr if isinstance(o, dict) and str(o.get("key")) in want}
    except Exception as e:
        print(f"  [govaffairs-ai] {e}")
        return {}


def _web_snippet(company):
    """Firecrawl search API -> top snippet + url for a company's gov-affairs footprint, or None.
    Opt-in: needs FIRECRAWL_API_KEY. Non-fatal; a search API (not a headless browser) so it runs
    from CI datacenter IPs without captchas."""
    key = os.environ.get("FIRECRAWL_API_KEY")
    if not key:
        return None
    q = dc.GOVAFFAIRS_WEB_QUERY.format(company=company)
    body = json.dumps({"query": q, "limit": 2}).encode("utf-8")  # top-2 snippets = 2 credits/search
    req = urllib.request.Request(dc.FIRECRAWL_SEARCH_URL, data=body,
                                 headers={"Authorization": f"Bearer {key}",
                                          "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.loads(r.read().decode("utf-8", "ignore"))
        for hit in d.get("data", []) or []:
            desc = hit.get("description") or hit.get("markdown") or hit.get("title") or ""
            if desc:
                return {"text": f"{hit.get('title', '')} — {desc}"[:600], "url": hit.get("url", "")}
    except Exception as e:
        print(f"  [govaffairs-web] {company}: {e}")
    return None


def _set(row, flag, source, url, evidence):
    row["inhouse_govaffairs"] = flag
    row["govaffairs_source"] = source
    row["govaffairs_evidence_url"] = url
    row["govaffairs_evidence"] = evidence


# --- entry point -----------------------------------------------------------
def attach(ranked, tabs, classify_fn=_llm_classify, web_fn=_web_snippet):
    """Set inhouse_govaffairs (+ source/url/evidence) on every ranked prospect. Cache-first;
    only NEW scraped items hit the LLM; web lookups only for still-unknown, capped, once-ever.
    Returns the count flagged True. classify_fn/web_fn are injectable for the self-check."""
    cache = load_cache()
    items, companies = cache["items"], cache["companies"]
    curated = {_norm(c) for c in dc.HAS_INHOUSE_GOVAFFAIRS}

    companies_lc = {_norm(r["company"]): r["company"] for r in ranked if r.get("company")}

    # 1) curated — Workday giants we can't scrape; always works offline.
    for r in ranked:
        if _norm(r.get("company")) in curated:
            _set(r, True, "curated", "", "known in-house India government-affairs team")

    # 2+3) gather NEW job/news rows for prospect companies, pre-gated, not yet in item cache.
    pending = []          # items to classify this run
    ev_by_key = {}        # key -> (company, source, url, snippet) for rollup
    ss1, ss2, ss4 = tabs.get("ss1") or [], tabs.get("ss2") or [], tabs.get("ss4") or []

    def _consider(item_key, actor, kind, text, url):
        if item_key in items:                       # judged before -> permanent verdict
            return
        if not _is_govaffairs_role(text):           # cheap pre-gate
            return
        co = _match_company(actor, companies_lc)
        if not co:
            return
        pending.append({"key": item_key, "company": co, "kind": kind, "text": text})
        ev_by_key[item_key] = (co, kind, url, text[:200])

    for r in ss4:
        if r.get("signal_type") == "job-posting":
            _consider(f"job:{r.get('id')}", r.get("actor"), "job",
                      r.get("excerpt") or "", r.get("url") or "")
    for r in ss1 + ss2:
        _consider(f"news:{r.get('id')}", r.get("title") or r.get("summary") or "", "news",
                  f"{r.get('title', '')} {r.get('summary', '')}", r.get("url") or "")

    verdicts = classify_fn(pending) if pending else {}
    for k, gov in verdicts.items():
        items[k] = gov                              # cache every judged item permanently

    # rollup: any positive item flags its company (evidence = that item).
    for k, (co, kind, url, snippet) in ev_by_key.items():
        if items.get(k):
            for r in ranked:
                if _norm(r.get("company")) == _norm(co) and not r.get("inhouse_govaffairs"):
                    _set(r, True, kind, url, snippet)

    # persist sticky company verdicts from cache for anything decided a prior run.
    for r in ranked:
        co_lc = _norm(r.get("company"))
        if not r.get("inhouse_govaffairs") and companies.get(co_lc, {}).get("flag"):
            c = companies[co_lc]
            _set(r, True, c.get("source", ""), c.get("evidence_url", ""), c.get("evidence", ""))

    # 4) web — only prospects STILL unknown, capped per-run AND per-month, never re-queried.
    month = str(date.today())[:7]
    usage = cache["usage"]
    budget = min(WEB_LOOKUP_MAX, WEB_LOOKUP_MONTHLY_MAX - usage.get(month, 0))
    web_pending = []
    for r in ranked:
        co_lc = _norm(r.get("company"))
        if r.get("inhouse_govaffairs") or f"web:{co_lc}" in items or budget <= 0:
            continue
        snip = web_fn(r["company"])
        items[f"web:{co_lc}"] = False               # attempted -> don't re-query (updated if True)
        budget -= 1
        usage[month] = usage.get(month, 0) + 1
        if snip and _is_govaffairs_role(snip["text"]):
            web_pending.append({"key": f"web:{co_lc}", "company": r["company"],
                                "kind": "web", "text": snip["text"]})
            ev_by_key[f"web:{co_lc}"] = (r["company"], "web", snip["url"], snip["text"][:200])
    for k, gov in (classify_fn(web_pending) if web_pending else {}).items():
        items[k] = gov
        if gov:
            co, kind, url, snippet = ev_by_key[k]
            for r in ranked:
                if _norm(r.get("company")) == _norm(co):
                    _set(r, True, kind, url, snippet)

    # write sticky company verdicts + defaults back to cache.
    flagged = 0
    for r in ranked:
        co_lc = _norm(r.get("company"))
        if r.get("inhouse_govaffairs"):
            flagged += 1
            companies.setdefault(co_lc, {
                "flag": True, "source": r.get("govaffairs_source", ""),
                "evidence_url": r.get("govaffairs_evidence_url", ""),
                "evidence": r.get("govaffairs_evidence", ""),
                "first_seen": str(date.today())})
        else:
            _set(r, False, "", "", "")

    save_cache(cache)
    return flagged


# --- self-check (network-free: stubs the LLM + web) ------------------------
def demo():
    dc.HAS_INHOUSE_GOVAFFAIRS  # noqa — must exist
    global CACHE_PATH
    CACHE_PATH = os.path.join(os.path.dirname(__file__), "tmp", "_govaffairs_selfcheck.json")
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    if os.path.exists(CACHE_PATH):
        os.remove(CACHE_PATH)

    ranked = [{"company": "Google"},           # curated
              {"company": "AirTrunk"},         # job-posting hit
              {"company": "Sify"},             # nothing -> web says yes
              {"company": "Nxtra"}]            # nothing anywhere -> False
    tabs = {
        "ss4": [{"signal_type": "job-posting", "id": "j1", "actor": "airtrunk",
                 "excerpt": "Head of Government Affairs, India — Mumbai", "url": "http://x/j1"},
                {"signal_type": "job-posting", "id": "j2", "actor": "airtrunk",
                 "excerpt": "Data Centre Engineer — Mumbai", "url": "http://x/j2"}],  # pre-gated out
        "ss1": [], "ss2": [],
    }

    def fake_classify(items):
        # LLM says gov=true for anything that reached it (all pre-gated to real gov roles here).
        return {it["key"]: True for it in items}

    def fake_web(company):
        return ({"text": "Sify names Head of Public Policy India", "url": "http://x/sify"}
                if company == "Sify" else None)

    n = attach(ranked, tabs, classify_fn=fake_classify, web_fn=fake_web)
    by = {r["company"]: r for r in ranked}
    assert by["Google"]["inhouse_govaffairs"] and by["Google"]["govaffairs_source"] == "curated"
    assert by["AirTrunk"]["inhouse_govaffairs"] and by["AirTrunk"]["govaffairs_source"] == "job"
    assert by["AirTrunk"]["govaffairs_evidence_url"] == "http://x/j1"
    assert by["Sify"]["inhouse_govaffairs"] and by["Sify"]["govaffairs_source"] == "web"
    assert not by["Nxtra"]["inhouse_govaffairs"]
    assert n == 3, n

    # stickiness: a 2nd run with NO evidence keeps prior verdicts, and re-judges nothing new.
    calls = []
    ranked2 = [{"company": c} for c in ("Google", "AirTrunk", "Sify", "Nxtra")]
    attach(ranked2, {"ss1": [], "ss2": [], "ss4": []},
           classify_fn=lambda it: calls.append(it) or {}, web_fn=lambda c: None)
    by2 = {r["company"]: r for r in ranked2}
    assert by2["AirTrunk"]["inhouse_govaffairs"], "sticky company verdict lost"
    assert by2["Sify"]["inhouse_govaffairs"], "sticky web verdict lost"
    assert calls == [[]] or calls == [], f"re-judged cached items: {calls}"

    os.remove(CACHE_PATH)
    print("dc_govaffairs self-check OK")


if __name__ == "__main__":
    demo()
