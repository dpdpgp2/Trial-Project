"""
dc_operators.py  —  Feature B: value-chain operator discovery -> Proposed queue -> promote.

Rides free on dc_spotlight's `orgs` (News + Disclosure rankers already extracted them).
This module NEVER scores or auto-adds: it writes only to the mutable `Proposed Operators`
store; a human promotes via the dashboard (dashboard/api/promote.js drops a GitHub Issue),
and the NEXT run reads approved issues, flips the row to status=approved, and RUNTIME-UNIONS
the name into the effective watchlist. Config lists stay the seed; the sheet is the store.

Verification is FREE registry/HTTP lookups (off the LLM budget), stop-at-first-hit:
  MCA (India, CIN) -> EDGAR (foreign filer) -> Wikidata (open-web tail).
Firecrawl is the credit-capped last resort — OFF by default at proposal time (Phase 5 lock).

Promotable = operators only (the names TAG can advise); suppliers (energy/cooling/hardware/
transmission) are surfaced as context but never promoted. Non-fatal throughout.
"""
import os
import json
import time
import urllib.request
import urllib.parse
from datetime import datetime, timezone, date

import dc_config as dc
import dc_mca

HEADER = ["name", "segment", "evidence_url", "status", "first_seen", "verified_by"]
LABEL = dc.PROMOTE_ISSUE_LABEL


def _today():
    return datetime.now(timezone.utc).date()


def _norm(name):
    return " ".join((name or "").lower().split())


def _promotable(segment):
    """Only operators become promotable prospects; suppliers are context only."""
    return (segment or "").strip().lower() == "operator"


# --------------------------------------------------------------- verify chain (free)
def _edgar_lookup(name):
    """Substring match against SEC's public company_tickers.json (cached). -> url|None."""
    ua = os.environ.get("SEC_USER_AGENT")
    if not ua:
        return None
    tickers = _sec_tickers(ua)
    low = _norm(name)
    for rec in tickers:
        if low and low in _norm(rec.get("title")):
            cik = str(rec.get("cik_str") or "").zfill(10)
            return f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}"
    return None


_SEC_TICKERS = None


def _sec_tickers(ua):
    global _SEC_TICKERS
    if _SEC_TICKERS is not None:
        return _SEC_TICKERS
    try:
        req = urllib.request.Request("https://www.sec.gov/files/company_tickers.json",
                                     headers={"User-Agent": ua})
        with urllib.request.urlopen(req, timeout=25) as r:
            data = json.loads(r.read().decode("utf-8", "ignore"))
        _SEC_TICKERS = list(data.values()) if isinstance(data, dict) else []
    except Exception as e:
        print(f"  [operators] edgar tickers non-fatal: {e}")
        _SEC_TICKERS = []
    return _SEC_TICKERS


def _wikidata_lookup(name):
    """Free, no-key entity search. -> concept URL | None."""
    try:
        url = ("https://www.wikidata.org/w/api.php?action=wbsearchentities&format=json"
               f"&language=en&type=item&limit=1&search={urllib.parse.quote(name)}")
        req = urllib.request.Request(url, headers={"User-Agent": "dc-operators"})
        time.sleep(0.2)
        with urllib.request.urlopen(req, timeout=20) as r:
            hits = json.loads(r.read().decode("utf-8", "ignore")).get("search") or []
        return hits[0].get("concepturi") if hits else None
    except Exception as e:
        print(f"  [operators] wikidata non-fatal: {e}")
        return None


def verify(name, mca_cache):
    """Stop-at-first-hit free chain -> (verified_by, evidence_url). ('', '') if none.
    Firecrawl (credit-capped) is intentionally NOT called here — promote-time only."""
    try:
        rec = dc_mca.resolve(name, mca_cache)
        if rec and rec.get("cin"):
            return "mca", ""
    except Exception as e:
        print(f"  [operators] mca non-fatal: {e}")
    u = _edgar_lookup(name)
    if u:
        return "edgar", u
    u = _wikidata_lookup(name)
    if u:
        return "wikidata", u
    return "", ""


# ----------------------------------------------------------- proposed store (sheet)
def _known_names(register):
    seed = set(dc.WATCH_OPERATORS_INDIA + dc.WATCH_OPERATORS_GCC + dc.WATCH_OPERATORS_FOREIGN)
    tracked = {(m.get("company") or "") for m in (register or {}).values()}
    return {_norm(n) for n in (seed | tracked) if n}


def _collect_orgs(spotlight):
    """New value-chain names from the News + Disclosure rankers' `orgs`, deduped by name."""
    out = {}
    for feed in ("ss1", "ss3"):
        v = (spotlight or {}).get(feed) or {}
        for o in v.get("orgs") or []:
            name = (o.get("name") or "").strip()
            if name and _norm(name) not in out:
                out[_norm(name)] = {"name": name, "segment": (o.get("segment") or "").strip().lower()}
    return out


def _expire(rows, today):
    """Drop un-promoted rows older than the stale window; keep approved forever."""
    keep = []
    for r in rows:
        if (r.get("status") or "").lower() == "approved":
            keep.append(r)
            continue
        try:
            age = (today - date.fromisoformat((r.get("first_seen") or "")[:10])).days
        except Exception:
            age = 0
        if age <= dc.PROPOSED_OPERATORS_STALE_DAYS:
            keep.append(r)
    return keep


def _gh(method, path, token, body=None):
    req = urllib.request.Request(
        "https://api.github.com" + path,
        data=json.dumps(body).encode() if body is not None else None, method=method,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
                 "User-Agent": "dc-pipeline"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8", "ignore") or "null")


def _read_approved_issues(token, repo):
    """Open promote-operator issues -> ([{name,segment,evidence_url}], [issue]). ([],[]) on fail."""
    try:
        issues = _gh("GET", f"/repos/{repo}/issues?labels={LABEL}&state=open&per_page=50", token)
    except Exception as e:
        print(f"  [operators] issue read non-fatal: {e}")
        return [], []
    approved, objs = [], []
    for it in issues or []:
        body = it.get("body") or ""
        import re
        m = re.search(r"\{.*\}", body, re.S)
        if not m:
            continue
        try:
            d = json.loads(m.group(0))
        except Exception:
            continue
        if d.get("name"):
            approved.append({"name": d["name"].strip(), "segment": (d.get("segment") or "").lower(),
                             "evidence_url": d.get("evidence_url") or ""})
            objs.append(it)
    return approved, objs


def _close_issue(issue, token, repo, note):
    n = issue.get("number")
    try:
        _gh("POST", f"/repos/{repo}/issues/{n}/comments", token, {"body": note})
        _gh("PATCH", f"/repos/{repo}/issues/{n}", token, {"state": "closed"})
    except Exception as e:
        print(f"  [operators] close #{n}: {e}")


def _write_tab(ss, rows):
    if ss is None:
        return
    try:
        import dc_sheets
        ws = dc_sheets.get_tab(ss, dc.PROPOSED_OPERATORS_TAB, HEADER)
        grid = [HEADER] + [[r.get(k, "") for k in HEADER] for r in rows]
        dc_sheets._retry(ws.clear)
        dc_sheets._retry(ws.update, "A1", grid, value_input_option="RAW")
    except Exception as e:
        print(f"  [operators] sheet write non-fatal: {e}")


def effective_watchlist(proposed_rows):
    """Runtime union: config seed lists + approved proposed names. The pipeline calls this
    to expand matching for free the moment a name is approved (config lists never mutate)."""
    seed = list(dc.WATCH_OPERATORS_INDIA + dc.WATCH_OPERATORS_GCC + dc.WATCH_OPERATORS_FOREIGN)
    have = {_norm(n) for n in seed}
    for r in proposed_rows:
        if (r.get("status") or "").lower() == "approved" and _norm(r.get("name")) not in have:
            seed.append(r.get("name"))
            have.add(_norm(r.get("name")))
    return seed


def union_watchlist(ss):
    """Runtime union BEFORE ranking: extend dc_score.OPERATORS (a module list the config
    seed can't rewrite) with approved Proposed-Operators names, in-memory this run only.
    This is what makes 'promote -> matched next run' take effect. Non-fatal, idempotent."""
    try:
        import dc_sheets
        import dc_score
        rows = dc_sheets.read_tab(ss, dc.PROPOSED_OPERATORS_TAB) if ss is not None else []
        have = {_norm(n) for n in dc_score.OPERATORS}
        added = 0
        for r in rows:
            if (r.get("status") or "").lower() == "approved" and _norm(r.get("name")) not in have:
                dc_score.OPERATORS.append(r["name"])
                have.add(_norm(r["name"]))
                added += 1
        if added:
            print(f"  Operators -> unioned {added} approved name(s) into the watchlist")
        return added
    except Exception as e:
        print(f"  [operators] union non-fatal: {e}")
        return 0


def run(ss, spotlight, register=None):
    """Read store -> expire -> add newly-discovered+verified orgs -> merge approved issues ->
    write store + close issues. -> {"proposed": [rows], "watchlist": [names]}. Never raises."""
    try:
        import dc_sheets
        today = _today()
        rows = dc_sheets.read_tab(ss, dc.PROPOSED_OPERATORS_TAB) if ss is not None else []
        rows = _expire(rows, today)
        by_name = {_norm(r.get("name")): r for r in rows}

        # 1. discover new names from this run's spotlight orgs (dedup vs store + known names)
        known = _known_names(register)
        mca_cache = dc_mca.load_cache()
        added = 0
        for key, o in _collect_orgs(spotlight).items():
            if key in by_name or key in known:
                continue
            verified_by, ev_url = verify(o["name"], mca_cache)
            row = {"name": o["name"], "segment": o["segment"], "evidence_url": ev_url,
                   "status": "proposed", "first_seen": today.isoformat(), "verified_by": verified_by}
            by_name[key] = row
            rows.append(row)
            added += 1
        dc_mca.save_cache(mca_cache)

        # 2. merge human promotions (open promote-operator issues) -> status=approved, close them
        token = os.environ.get("GITHUB_TOKEN")
        repo = os.environ.get("GITHUB_REPOSITORY") or "dpdpgp2/Trial-Project"
        promoted = 0
        if token and ss is not None:
            approved, objs = _read_approved_issues(token, repo)
            for a, issue in zip(approved, objs):
                key = _norm(a["name"])
                r = by_name.get(key)
                if r is None:
                    r = {"name": a["name"], "segment": a["segment"] or "operator",
                         "evidence_url": a["evidence_url"], "first_seen": today.isoformat(),
                         "verified_by": ""}
                    rows.append(r)
                    by_name[key] = r
                r["status"] = "approved"
                promoted += 1
                _close_issue(issue, token, repo, f"Promoted `{a['name']}` — unioned into the watchlist next run.")

        _write_tab(ss, rows)
        watch = effective_watchlist(rows)
        print(f"  Operators -> {len(rows)} proposed (+{added} new, {promoted} promoted); "
              f"watchlist {len(watch)}")
        return {"proposed": rows, "watchlist": watch}
    except Exception as e:
        print(f"  [operators] non-fatal: {e}")
        return {"proposed": [], "watchlist": effective_watchlist([])}


# --------------------------------------------------------------------- self-check
def demo():
    """Network-free self-check. Stubs verify sources, the sheet, and GitHub."""
    import dc_operators as M

    store = []                                       # fake sheet: list of row dicts
    import dc_sheets
    dc_sheets.read_tab = lambda ss, tab: list(store)

    # verify: novel "NovaEdge DC" resolves via edgar; "GhostCo" nowhere; suppliers verify too
    M._edgar_lookup = lambda n: "https://sec.gov/x" if n == "NovaEdge DC" else None
    M._wikidata_lookup = lambda n: None
    dc_mca.resolve = lambda n, c: None
    dc_mca.load_cache = lambda: {}
    dc_mca.save_cache = lambda c: None

    spot = {
        "ss1": {"orgs": [{"name": "NovaEdge DC", "segment": "operator"},       # novel, verifies via edgar
                         {"name": "GhostCo", "segment": "operator"},           # promotable, unverified
                         {"name": "CoolFluid Inc", "segment": "cooling/coolant"},  # supplier -> context only
                         {"name": "CtrlS", "segment": "operator"}]},           # already in seed -> dedup
        "ss3": {"orgs": [{"name": "NovaEdge DC", "segment": "operator"}]},     # cross-feed dedup
    }
    r = M.run(None, spot, register={})
    names = {row["name"] for row in r["proposed"]}
    assert "CtrlS" not in names, "seed watchlist name not deduped"
    assert {"NovaEdge DC", "GhostCo", "CoolFluid Inc"} <= names, "discovery missed a new org"
    assert len(names) == 3, f"cross-feed dedup failed: {names}"
    nova = next(x for x in r["proposed"] if x["name"] == "NovaEdge DC")
    assert nova["verified_by"] == "edgar", "verify chain did not record source"
    assert M._promotable("operator") and not M._promotable("cooling/coolant"), "promotable filter wrong"
    assert "NovaEdge DC" not in effective_watchlist(r["proposed"]), "unapproved name leaked into watchlist"

    # expiry: a stale un-promoted row drops; an approved one survives
    old = (M._today().replace(year=M._today().year - 1)).isoformat()
    aged = [{"name": "StaleCo", "segment": "operator", "status": "proposed", "first_seen": old,
             "evidence_url": "", "verified_by": ""},
            {"name": "KeepCo", "segment": "operator", "status": "approved", "first_seen": old,
             "evidence_url": "", "verified_by": "mca"}]
    kept = {r2["name"] for r2 in M._expire(aged, M._today())}
    assert kept == {"KeepCo"}, f"expiry wrong: {kept}"
    assert "KeepCo" in effective_watchlist(aged), "approved name not unioned into watchlist"

    # union_watchlist: an approved sheet row is appended to dc_score.OPERATORS in-memory
    import dc_score
    dc_sheets.read_tab = lambda ss, tab: [
        {"name": "UnionCo", "segment": "operator", "status": "approved", "first_seen": old,
         "evidence_url": "", "verified_by": "mca"}]
    before = len(dc_score.OPERATORS)
    M.union_watchlist(object())                       # any non-None ss triggers the read
    assert "UnionCo" in dc_score.OPERATORS, "approved name not unioned into scoring watchlist"
    assert M.union_watchlist(object()) == 0, "union not idempotent"       # already present
    dc_score.OPERATORS[:] = dc_score.OPERATORS[:before]                    # leave global clean

    print("dc_operators self-check OK")


if __name__ == "__main__":
    demo()
