"""
dc_spotlight.py  —  per-feed "Most Important — last 48h" AI highlight + value-chain
operator extraction (Feature A + Feature B data). Mirrors dc_ai.triangulate():
cached, id-validated, non-fatal. Never kills the pipeline.

Per run (SS1 News, SS2 Policy, SS3 Disclosure — OSINT excluded):
  1. filter each feed to the last SPOTLIGHT_DAYS by row date; empty feed -> skip, no call.
  2. attach the ALREADY-COMPUTED deal_usd bucket (dc_bd._deal_usd) + matched state
     (dc_states.map_state) to each candidate row — grounding, not headline-guessing.
  3. hash (feed's in-window rows + today); unchanged feed -> serve cached, NO call.
  4. one ranker call per changed feed -> top SPOTLIGHT_MAX_PER_FEED by BD relevance,
     grounded on docs/TAG_BD_CRITERIA.md. News + Disclosure rankers also emit `orgs`.
  5. id-validate every returned id against that feed's real input rows (drop fabricated).
  6. ONE judge call over all fresh picks -> per-feed useful|widen. Each `widen` feed:
     loosen the relevance bar INSIDE the 48h window, re-rank, re-judge (<= SPOTLIGHT_MAX_WIDEN).

A failure anywhere -> deterministic (deal-bucket + recency) fallback and/or last-good result.
Grounding rubric passed verbatim: docs/TAG_BD_CRITERIA.md.
"""
import os
import hashlib
from datetime import datetime, timezone, timedelta

import dc_config as dc
import dc_bd
import dc_states
# Reused verbatim from dc_ai (module-level so demo() can monkeypatch _chat/test_connection):
from dc_ai import (_chat, _json_obj, load_cache, save_cache,   # noqa: F401
                   _parse_date, _now, test_connection)

CRITERIA_PATH = os.path.join(os.path.dirname(__file__), "docs", "TAG_BD_CRITERIA.md")
_SCHEMA = "v6-events"    # bump when item shape OR ranker prompt/call changes (busts the per-feed cache)
_ORG_FEEDS = ("ss1", "ss3")   # only News + Disclosure rankers extract value-chain orgs
_HIGH, _MED = dc.FEE_VIABILITY_DEAL_USD["high"], dc.FEE_VIABILITY_DEAL_USD["medium"]


def _criteria():
    """The grounding rubric, verbatim. Small inline fallback if the doc is missing."""
    try:
        with open(CRITERIA_PATH, encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ("TAG sells India market-entry advisory (~$600k/yr retainer). Rank high: "
                "cross-border movers (foreign/GCC entering India), deals >=$50M ($500M strong) "
                "or mega-fund/sovereign backers, active triggers (land/capex/JV/energy), P1 "
                "states (Maharashtra, Uttar Pradesh, Telangana, Tamil Nadu, Andhra Pradesh). "
                "Drop hyperscalers-as-client (AWS/Amazon/Microsoft/Google/Oracle/Meta), "
                "entrenched domestic incumbents, sub-$50M chatter. Affordability is a gate, "
                "not the axis — a small novel cross-border first-mover still ranks.")


def _state_matrix_line():
    try:
        rows = sorted(dc_states.targeting_matrix(), key=lambda r: r["priority"])
        return "STATE TARGETING (P1 = most attractive): " + " · ".join(
            f"{r['state']} [{r['priority']}]" for r in rows)
    except Exception:
        return ""


def _deal_bucket(text):
    usd = dc_bd._deal_usd(text)
    return "≥$500M" if usd >= _HIGH else "≥$50M" if usd >= _MED else ""


# feed -> (id_field, date_field, text-builder). Policy rows carry no deal value.
_FEED_SPEC = {
    "ss1": ("id", "date",
            lambda r: f"{r.get('title', '')} {r.get('summary', '')} {r.get('entities', '')}"),
    "ss2": ("id", "date",
            lambda r: f"{r.get('title', '')} {r.get('summary', '')} {r.get('policy_class', '')}"),
    "ss3": ("accession", "filed_date",
            lambda r: f"{r.get('filer', '')} {r.get('relevance', '')} {r.get('evidence', '')}"),
}


def _window_days(feed):
    return dc.SPOTLIGHT_FEED_WINDOW.get(feed, dc.SPOTLIGHT_DAYS)


def _candidates(feed, rows, today):
    """In-window rows for one feed, each pre-tagged with deal bucket + matched state.
    Per-feed horizon (News 48h, Policy/Disclosure 30d) and per-feed row budget (the latest
    N rows sent to the ranker). -> [{id, date, url, text, title, deal, state}] newest first."""
    idf, datef, textf = _FEED_SPEC[feed]
    cutoff = today - timedelta(days=_window_days(feed))
    out = []
    for r in rows:
        rid = str(r.get(idf) or "").strip()
        d = _parse_date(r.get(datef))
        if not rid or not d or d < cutoff:
            continue
        text = " ".join((textf(r) or "").split())
        # title used for near-duplicate detection (same story from many sources -> one pick).
        # SS3 folds in the unique accession so distinct filings never merge.
        title = (r.get("title") or "").strip() if feed != "ss3" \
            else f"{r.get('filer', '')} {rid}"
        out.append({
            "id": rid,
            "date": d.isoformat(),
            "url": r.get("url") or "",
            "text": text[:220],
            "title": title,
            "deal": "" if feed == "ss2" else _deal_bucket(text),
            "state": ", ".join(dc_states.map_state(text)),
        })
    out.sort(key=lambda c: c["date"], reverse=True)
    return out[: dc.SPOTLIGHT_FEED_ROWS.get(feed, 400)]


def _known_names():
    names = set(dc.WATCH_OPERATORS_INDIA + dc.WATCH_OPERATORS_GCC + dc.WATCH_OPERATORS_FOREIGN)
    return {n.lower() for n in names}


RANK_SYSTEM = (
    "detailed thinking off\n\n"
    "You are a business-development analyst for The Asia Group (TAG). Rank the recent rows (last "
    "{window} days) of ONE data-stream by BD relevance for TAG, grounded ONLY on the CRITERIA below and the rows "
    "given. Never invent companies, deals, states, or ids — copy every row id (r1, r2, …) exactly; "
    "invented ids are deleted by a validator.\n\n"
    "{feedhint}"
    "=== TAG BD CRITERIA (verbatim grounding) ===\n{criteria}\n\n{states}\n\n"
    "Each row is pre-tagged with a deterministic deal bucket (deal=) and matched state (state=) — "
    "judge deal value and state attractiveness on THOSE, not on headline-guessing.\n"
    "FIRST cluster the rows into EVENTS. Group two rows into ONE event ONLY when they report the SAME "
    "announcement by the SAME company/project — even if outlets word the headline differently or name "
    "the state vs its city (e.g. 'Odisha' and its capital 'Bhubaneswar'). NEVER merge DIFFERENT "
    "companies, different projects, or unrelated stories into one event — those are SEPARATE events "
    "(e.g. an HCLTech Odisha build and a Ping Identity launch and a TCS land deal are THREE events, "
    "never one). List ALL row ids in each event; every row id appears in AT MOST ONE event.\n"
    "THEN return the TOP {maxn} most important DATA-CENTRE events of the window, RANKED by BD relevance. "
    "This is a FULL top-{maxn} briefing, not a shortlist — surface the desk's whole picture:\n"
    "  • tier='opportunity' — a genuine TAG India-market-entry play: a cross-border mover INTO India, a "
    "real trigger (land/capex/JV/energy), an attractive state. Rank these FIRST.\n"
    "  • tier='context' — other notable DC news worth knowing but NOT a direct TAG India-entry play: US / "
    "global deals, hyperscaler moves, India market milestones, GCC/Saudi builds. Rank these BELOW the "
    "opportunities, still by importance.\n"
    "Order: all opportunities first (most relevant first), then context. FILL UP TO {maxn} events when the "
    "window holds that many real DC stories. Drop ONLY pure market-research / vendor spam (e.g. headlines "
    "like 'X Market Forecast/Size/Analysis', 'Adaptor Market', 'AC Fans Market') and non-data-centre "
    "noise. Weigh relevance by: cross-border motion (foreign/GCC->India) heaviest, then deal bucket, then "
    "P1-state + valid policy, then trigger freshness/novelty.{loosen}{orgs}\n\n"
    "OUTPUT — ONLY this JSON object, no prose, no markdown fences:\n"
    '{{"items":[{{"heading":"<one-line event heading, <=120 chars>",'
    '"tier":"opportunity"|"context",'
    '"reason":"<one line, <=160 chars, why this event matters to TAG>",'
    '"criteria_hits":["cross-border"|"deal"|"P1-state"|"trigger"|"novel"],'
    '"article_ids":["<id copied exactly>", ...]}}]{orgs_schema}}}'
)
# Per-feed framing: the ranker is news/deal-shaped by default, so tell it how to read the
# slower feeds (policy items and regulatory filings are events too, not just headlines).
_FEED_HINT = {
    "ss2": ("FEED = POLICY. These rows are state/central data-centre POLICY items (incentive "
            "schemes, GOs, rules, land/power terms). A new or updated DC policy IS an event — "
            "rank by state attractiveness (P1 first) and how actionable it is for a TAG client.\n\n"),
    "ss3": ("FEED = DISCLOSURES. These rows are SEC/regulatory FILINGS, not news. Treat ANY filing "
            "showing a real data-centre signal (capacity commitment, capex, India/GCC exposure, "
            "expansion, JV) as an event — a SINGLE filing is a valid event. Low-confidence or "
            "hyperscaler filings are tier='context', NOT dropped. Drop only filings with genuinely "
            "no data-centre content.\n\n"),
}
_LOOSEN = ("\nRELEVANCE BAR LOOSENED: the strict pass found too little — include weaker-but-real "
           "rows this time, but STAY inside the given window and still drop pure noise.")
_ORGS_INSTR = ("\nALSO extract DC value-chain company NAMES mentioned in these rows, each tagged by "
               "segment (operator | energy/power | cooling/coolant | hardware/compute | "
               "transmission/network). Names only — do not invent, do not include ids.")
_ORGS_SCHEMA = ',"orgs":[{"name":"<company>","segment":"<segment>"}]'

JUDGE_SYSTEM = (
    "detailed thinking off\n\n"
    "You review a per-feed 'Most Important — last 48h' pick list before it reaches a BD "
    "decision-maker. For EACH feed judge usefulness + stream health only: are the picks concrete, "
    "BD-relevant TAG opportunities from a healthy stream ('useful'), or technically-real-but-useless / "
    "a broken-or-stale stream that should be re-ranked with a looser bar ('widen')? Do NOT invent.\n"
    'Output ONLY JSON: {"feeds":{"<feed>":"useful"|"widen", ...}}'
)


def _rank_feed(key, feed, cands, loosen=False):
    """One ranker call -> ([items], [orgs]). id-validated against `cands`. Raises on call error."""
    want_orgs = feed in _ORG_FEEDS
    system = RANK_SYSTEM.format(
        criteria=_criteria(), states=_state_matrix_line(), maxn=dc.SPOTLIGHT_MAX_PER_FEED,
        window=_window_days(feed), feedhint=_FEED_HINT.get(feed, ""),
        loosen=_LOOSEN if loosen else "",
        orgs=_ORGS_INSTR if want_orgs else "", orgs_schema=_ORGS_SCHEMA if want_orgs else "")
    # Short SURROGATE ids (r1, r2, …) instead of raw ids: SS3 accessions like
    # "0001575872-26-000526" are long and the model mangles them when echoing, which would
    # drop every event at id-validation. The model only ever handles r-ids; we map back here.
    sur = {f"r{i + 1}": c["id"] for i, c in enumerate(cands)}
    user = "ROWS (id | date | state | deal | text):\n" + "\n".join(
        f"r{i + 1} | {c['date']} | {c['state'] or '-'} | {c['deal'] or '-'} | {c['text']}"
        for i, c in enumerate(cands))
    obj = _json_obj(_chat(key, system, user, max_tokens=1500, temperature=0.1))
    return _validate_items(obj, cands, want_orgs, sur)


def _validate_items(obj, cands, want_orgs, sur=None):
    """LLM-clustered EVENTS: map surrogate ids back to real ids, keep only real ids, each id in
    one event only, drop empty events, clip, cap. The LLM does the clustering; this is the
    id-existence + no-double-count guard on top."""
    valid = {c["id"]: c for c in cands}
    sur = sur or {}
    items, used = [], set()
    for it in (obj.get("items") or []):
        if not isinstance(it, dict):
            continue
        ids, seen = [], set()
        for raw in (it.get("article_ids") or []):
            rid = sur.get(str(raw).strip(), str(raw).strip())   # surrogate -> real (or real as-is)
            if rid in valid and rid not in used and rid not in seen:
                seen.add(rid)
                ids.append(rid)
        if not ids:                                   # no real, unused article -> drop the event
            continue
        used.update(ids)
        hits = [str(h)[:24] for h in (it.get("criteria_hits") or [])][:5]
        tier = "opportunity" if str(it.get("tier") or "").lower() == "opportunity" else "context"
        items.append({"rank": len(items) + 1,
                      "heading": str(it.get("heading") or "")[:120], "tier": tier,
                      "reason": str(it.get("reason") or "")[:160],
                      "criteria_hits": hits, "article_ids": ids})
        if len(items) >= dc.SPOTLIGHT_MAX_PER_FEED:
            break
    orgs = _validate_orgs(obj) if want_orgs else []
    return items, orgs


def _validate_orgs(obj):
    """value-chain names, deduped against the seed watchlist, segment-checked, capped."""
    known = _known_names()
    segs = set(dc.OPERATOR_SEGMENTS)
    out, seen = [], set()
    for o in (obj.get("orgs") or []):
        if not isinstance(o, dict):
            continue
        name = str(o.get("name") or "").strip()
        seg = str(o.get("segment") or "").strip().lower()
        low = name.lower()
        if not name or low in known or low in seen or seg not in segs:
            continue
        seen.add(low)
        out.append({"name": name[:80], "segment": seg})
        if len(out) >= 20:
            break
    return out


def _judge(key, fresh):
    """fresh: {feed: (items, orgs)} -> {feed: 'useful'|'widen'}. Any failure -> all 'useful'."""
    if not fresh:
        return {}
    lines = []
    for feed, (items, _) in fresh.items():
        lines.append(f"[{feed}] {len(items)} events:")
        lines += [f"  - {it['heading']}: {it['reason']}" for it in items] or ["  (none)"]
    try:
        obj = _json_obj(_chat(key, JUDGE_SYSTEM, "\n".join(lines), max_tokens=400, temperature=0.0))
        verd = obj.get("feeds") or {}
        return {f: ("widen" if str(verd.get(f)).lower() == "widen" else "useful") for f in fresh}
    except Exception as e:
        print(f"  [spotlight] judge non-fatal: {e}")
        return {f: "useful" for f in fresh}


def _fallback_items(cands):
    """Deterministic ranking when the model is unavailable: deal bucket then recency. No LLM to
    cluster, so each event is a single article (heading = its title)."""
    order = {"≥$500M": 2, "≥$50M": 1, "": 0}
    ranked = sorted(cands, key=lambda c: (order.get(c["deal"], 0), c["date"]), reverse=True)
    return [{"rank": i + 1, "heading": (c.get("title") or "")[:120], "tier": "context",
             "reason": "", "criteria_hits": [], "article_ids": [c["id"]]}
            for i, c in enumerate(ranked[: dc.SPOTLIGHT_MAX_PER_FEED])]


def spotlight(ss, tabs, register=None):
    """Per-feed 48h highlight. Never raises.
    -> {feed: {generated_at, window_days, status, items, orgs}} or None (total failure)."""
    cache = load_cache()
    last = cache.get("spotlight") or {}
    try:
        today = datetime.now(timezone.utc).date()
        today_s = today.isoformat()
        hashes = cache.get("spot_hash") or {}

        cands = {f: _candidates(f, tabs.get(f) or [], today) for f in dc.SPOTLIGHT_FEEDS}
        result, need = {}, {}          # need: feeds requiring a fresh call
        for feed, cs in cands.items():
            if not cs:
                result[feed] = {"generated_at": _now(), "window_days": _window_days(feed),
                                "status": "empty", "items": [], "orgs": []}
                continue
            # _SCHEMA in the hash busts the cache when the output format changes (else a
            # same-day rerun serves last-good rows in an older schema the export can't read).
            h = hashlib.sha1((repr(cs) + today_s + _SCHEMA).encode("utf-8")).hexdigest()
            if hashes.get(feed) == h and last.get(feed):
                result[feed] = dict(last[feed], status="cached")
            else:
                need[feed] = h

        if need:
            key = os.environ.get("OPENROUTER_API_KEY")
            ok, note, _ = test_connection(key) if key else (False, "no key", None)
            if not ok:
                print(f"  Spotlight -> {note}; deterministic + last-good fallback")
                for feed in need:
                    result[feed] = last.get(feed) or {
                        "generated_at": _now(), "window_days": _window_days(feed),
                        "status": "fallback", "items": _fallback_items(cands[feed]),
                        "orgs": (last.get(feed) or {}).get("orgs", [])}
            else:
                fresh = {}
                for feed in need:
                    try:
                        fresh[feed] = _rank_feed(key, feed, cands[feed])
                    except Exception as e:
                        print(f"  [spotlight] {feed} ranker non-fatal: {e}")
                        result[feed] = last.get(feed) or {
                            "generated_at": _now(), "window_days": _window_days(feed),
                            "status": "fallback", "items": _fallback_items(cands[feed]), "orgs": []}
                # judge + bounded widen (loosen the bar INSIDE 48h; never extend window)
                pending = set(fresh)
                for _ in range(dc.SPOTLIGHT_MAX_WIDEN + 1):
                    if not pending:
                        break
                    verd = _judge(key, {f: fresh[f] for f in pending})
                    widen = {f for f in pending if verd.get(f) == "widen"}
                    pending = set()
                    for feed in widen:
                        try:
                            fresh[feed] = _rank_feed(key, feed, cands[feed], loosen=True)
                            pending.add(feed)      # re-judge the widened result
                        except Exception as e:
                            print(f"  [spotlight] {feed} widen non-fatal: {e}")
                for feed, (items, orgs) in fresh.items():
                    status = "ok" if items else "empty"
                    result[feed] = {"generated_at": _now(), "window_days": _window_days(feed),
                                    "status": status, "items": items, "orgs": orgs}
                for feed in need:
                    hashes[feed] = need[feed]

        cache.update({"spotlight": result, "spot_hash": hashes, "spot_ts": _now()})
        save_cache(cache)
        n = {f: len(v["items"]) for f, v in result.items()}
        print(f"  Spotlight -> {n} (windows {dc.SPOTLIGHT_FEED_WINDOW})")
        return result
    except Exception as e:
        print(f"  [spotlight] non-fatal: {e}")
        return last or None


# --------------------------------------------------------------------- self-check
def demo():
    """Network-free self-check. Stubs _chat + connection + cache; asserts locked semantics."""
    import dc_spotlight as M
    store = {}                                    # in-memory cache — never touch ai_cache.json
    M.load_cache = lambda: dict(store)
    M.save_cache = lambda c: (store.clear(), store.update(c))
    today = datetime.now(timezone.utc).date()
    d0 = today.isoformat()
    stale = (today - timedelta(days=10)).isoformat()
    tabs = {
        "ss1": [
            {"id": "n1", "date": d0, "title": "AirTrunk plans $5 billion Mumbai hyperscale campus",
             "summary": "foreign operator entering India", "url": "https://x/1", "entities": "AirTrunk"},
            {"id": "n2", "date": d0, "title": "Local vendor ships racks in Pune", "summary": "",
             "url": "https://x/2", "entities": ""},
            # same story from 2 more sources -> must collapse to ONE pick (event_id NOT used)
            {"id": "dupA", "date": d0, "title": "HCLTech to Build First India Data Centre in Odisha, Targets 2027",
             "summary": "", "url": "https://x/a", "entities": "HCLTech"},
            {"id": "dupB", "date": d0, "title": "HCLTech likely to build its first India data centre in Odisha",
             "summary": "", "url": "https://x/b", "entities": "HCLTech"},
            {"id": "nOld", "date": stale, "title": "Old news", "summary": "", "url": "https://x/3"},
        ],
        "ss2": [  # this feed the judge fails once, then passes after widen
            {"id": "p1", "date": d0, "title": "Telangana notifies data centre incentive",
             "summary": "", "policy_class": "incentive", "url": "https://x/p1"},
        ],
        "ss3": [],  # empty feed -> skipped, panel hidden
    }

    calls = {"rank": 0}
    judged = {"ss2": 0}

    def fake_chat(key, system, user, max_tokens, temperature=0.2, reason=False):
        if "review a per-feed" in system:                      # judge call
            # fail ss2 the first time it is judged, pass thereafter; ss1 always useful
            judged["ss2"] += 1
            v = "widen" if judged["ss2"] == 1 else "useful"
            feeds = {}
            for line in user.splitlines():
                if line.startswith("[") and "] " in line:
                    f = line[1:line.index("]")]
                    feeds[f] = v if f == "ss2" else "useful"
            import json as _j
            return _j.dumps({"feeds": feeds})
        calls["rank"] += 1                                     # ranker call
        # rows carry SURROGATE ids (r1, r2, …); cluster by TEXT (HCLTech), +a fabricated id.
        import json as _j
        parsed = [(ln.split(" | ")[0], ln.lower()) for ln in user.splitlines() if " | " in ln]
        hcl = [sid for sid, ln in parsed if "hcltech" in ln]
        events = []
        if len(hcl) >= 2:                                       # HCLTech story from 2 sources -> 1 event
            events.append({"heading": "HCLTech first India DC in Odisha", "tier": "opportunity",
                           "reason": "cross-border first-mover", "criteria_hits": ["cross-border", "trigger"],
                           "article_ids": hcl + ["GHOST"]})     # GHOST invented -> dropped
            rest = [sid for sid, _ in parsed if sid not in hcl]
        else:
            rest = [sid for sid, _ in parsed]
        for i in rest:                                          # no tier -> defaults to 'context'
            events.append({"heading": f"event {i}", "reason": "matters",
                           "criteria_hits": ["cross-border"], "article_ids": [i]})
        out = {"items": events}
        if '"orgs"' in system:
            out["orgs"] = [{"name": "AirTrunk", "segment": "operator"},   # dedup: seed watchlist
                           {"name": "NewCo Power", "segment": "energy/power"}]
        return _j.dumps(out)

    M._chat = fake_chat
    M.test_connection = lambda key: (True, "ok", 1000)
    os.environ["OPENROUTER_API_KEY"] = "test"
    r = M.spotlight(None, tabs)

    assert r["ss3"]["status"] == "empty" and not r["ss3"]["items"], "empty feed not skipped"
    ss1 = r["ss1"]["items"]
    all_ids = [i for it in ss1 for i in it["article_ids"]]
    assert "GHOST" not in all_ids, "fabricated id not dropped"
    assert "nOld" not in all_ids, "stale row not excluded"
    assert {"n1", "n2"} <= set(all_ids), "in-window rows missing"
    assert len(all_ids) == len(set(all_ids)), "an article was double-counted across events"
    hcl = [it for it in ss1 if set(it["article_ids"]) & {"dupA", "dupB"}]
    assert len(hcl) == 1 and set(hcl[0]["article_ids"]) == {"dupA", "dupB"}, "same story not clustered into one event"
    assert hcl[0]["tier"] == "opportunity", "tier not passed through"
    assert all(it["tier"] in ("opportunity", "context") for it in ss1), "tier missing/invalid"
    assert [it for it in ss1 if it["tier"] == "context"], "context tier not defaulted"
    orgs = {o["name"] for o in r["ss1"]["orgs"]}
    assert "AirTrunk" not in orgs and "NewCo Power" in orgs, "org dedup/extract wrong"
    assert not r["ss2"]["orgs"], "policy feed must not extract orgs"
    assert judged["ss2"] >= 2, "widen loop did not re-judge the failing feed"
    assert r["ss1"]["items"][0]["rank"] == 1, "rank not assigned"

    # second run over identical tabs -> everything cached, ZERO new ranker calls
    before = calls["rank"]
    r2 = M.spotlight(None, tabs)
    assert calls["rank"] == before, "cache miss on unchanged feeds"
    assert r2["ss1"]["status"] == "cached", "unchanged feed not served from cache"

    # deterministic fallback when no key
    M.test_connection = lambda key: (False, "no key", None)
    store.clear()                                              # force the call path (no cache hit)
    r3 = M.spotlight(None, tabs)
    assert r3["ss1"]["status"] == "fallback" and r3["ss1"]["items"], "no deterministic fallback"

    print("dc_spotlight self-check OK")


if __name__ == "__main__":
    demo()
