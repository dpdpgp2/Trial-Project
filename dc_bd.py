"""
dc_bd.py  —  the actionable layer. Turns ranked operators + presence + evidence into a
BD Pipeline (P1/P2/P3), independent of the Signal Score (a low-score company with a real
recent India deal is still P1). GCC-only operators go to a separate GCC Watch.

Hard columns are deterministic. Soft judgement columns (pain point / TAG wedge / buyer /
intro / next action) are AI-DRAFTED, grounded ONLY on sheet evidence, and every drafted
cell is prefixed "🤖AI-draft: " so the team sees exactly what's model-generated.
"""
import os
import json
import hashlib

import dc_config as dc
import dc_evidence

BD_HEADER = ["Priority", "Company", "Segment", "Trigger", "Why-now", "India stage",
             "Pain point", "TAG wedge", "Public buyer + role", "Intro path", "Confidence",
             "Next action", "Evidence", "Owner", "Status",
             # M7 (append-only): R3 BD Priority internals + fee viability
             "Role", "Type", "BD Score", "Factor breakdown", "Fee viability", "Source tiers"]
GCC_HEADER = ["company", "geo", "latest signal", "note"]
BD_CACHE = os.path.join(os.path.dirname(__file__), "bd_cache.json")
AI_MARK = "🤖AI-draft: "
_SOFT = [("Pain point", "pain_point"), ("TAG wedge", "tag_wedge"),
         ("Public buyer + role", "public_buyer"), ("Intro path", "intro_path"),
         ("Next action", "next_action")]

_BD_SYS = (
    "detailed thinking off\n\n"
    "You are a TAG (The Asia Group) business-development strategist. For each company you get a "
    "validated Trigger, India stage, and evidence snippets FROM THE SHEET ONLY. Draft five short "
    "fields, grounded ONLY in that data — no outside facts, no invented names or numbers:\n"
    "pain_point (the India challenge the trigger implies — state the problem, then ' — ' and the "
    "specific evidence line that supports it; <= 28 words), tag_wedge (TAG's specific service: "
    "market-entry / government & regulatory / state land+power coordination / partnerships), "
    "public_buyer (the Indian public/government stakeholder + role, ONLY if implied by the data, "
    "else empty), intro_path (how TAG reaches them; generic if unknown), next_action (one concrete "
    "step). Each field except pain_point <= 14 words.\n"
    "tag_wedge MUST match the India stage: established/scaling => expansion / government-affairs / "
    "partnership (NEVER 'market-entry'); announced or no-known-presence => market-entry.\n"
    "Output ONLY a JSON array: "
    '[{"company":"..","pain_point":"..","tag_wedge":"..","public_buyer":"..","intro_path":"..","next_action":".."}]'
)


def _india_relevant(r):
    return ("india" in (r.get("geo") or "").lower()
            or r.get("india_presence") not in (None, "", "unknown"))


def _priority(r):
    if r.get("all_t3"):                 # R2: all-T3 evidence can never exceed P3
        return "P3 Monitor"
    pres = r.get("india_presence")
    recent_trigger = bool(r.get("deal_value")) or int(r.get("partnership_strength") or 0) > 0
    if pres in ("established", "announced") and recent_trigger:
        return "P1 Act now"
    if _india_relevant(r) and float(r.get("momentum") or 0) >= 3:
        return "P2 Qualify"
    return "P3 Monitor"


def _t1_share(mix):
    """'T1:2 T2:4 T3:1' -> share of T1+T2 weighted toward T1 (source confidence 0-1)."""
    counts = {}
    for part in (mix or "").split():
        k, _, n = part.partition(":")
        try:
            counts[k] = int(n)
        except ValueError:
            pass
    total = sum(counts.values())
    if not total:
        return 0.4                                     # unknown mix: neutral-low
    return (counts.get("T1", 0) * 1.0 + counts.get("T2", 0) * 0.6) / total


def _signals_for(r, ss3_signals):
    """[(label, region)] from the SS3 `signals` column of this company's cited filings."""
    out = []
    for i in (r.get("top_evidence_ids") or "").split(","):
        for part in (ss3_signals or {}).get(i.strip(), "").split(";"):
            lab, _, reg = part.strip().partition("|")
            if lab in dc.SIGNAL_LABELS:
                out.append((lab, reg))
    return out


_USD_HIGH, _USD_MED = dc.FEE_VIABILITY_DEAL_USD["high"], dc.FEE_VIABILITY_DEAL_USD["medium"]


def _deal_usd(deal_value):
    """Rough USD bucket from a deal_value string ('$5 billion', 'Rs 15,266 crore')."""
    import re as _re
    m = _re.search(r"([\d,.]+)\s*(billion|bn|trillion|tn|million|mn|crore|cr|lakh)",
                   (deal_value or "").lower())
    if not m:
        return 0
    try:
        n = float(m.group(1).replace(",", ""))
    except ValueError:
        return 0
    unit = m.group(2)
    mult = {"billion": 1e9, "bn": 1e9, "trillion": 1e12, "tn": 1e12,
            "million": 1e6, "mn": 1e6, "crore": 1.2e5, "cr": 1.2e5, "lakh": 1.2e3}[unit]
    return n * mult


def fee_viability(r, entities=None):
    """(level, why) — TAG fee-bar check, computed ONLY for role Prospect/Partner
    (the ranked real prospects). Deterministic: curated backer scale + deal size
    + listed/paid-up capital from the Entities spine. No paid APIs."""
    if (r.get("role") or "") not in ("Prospect", "Partner"):
        return "", ""
    co = (r.get("company") or "").lower()
    reasons = []
    level = "unknown"
    for scale, names in dc.BACKER_SCALE.items():
        if any(co == n.lower() for n in names):
            level = "high" if scale in ("mega-fund", "hyperscaler") else "medium"
            reasons.append(f"{scale} backer-scale")
            break
    usd = _deal_usd(r.get("deal_value"))
    if usd >= _USD_HIGH:
        level = "high"
        reasons.append(f"deal ≥ $500M ({r.get('deal_value')})")
    elif usd >= _USD_MED and level != "high":
        level = "medium" if level == "unknown" else level
        reasons.append(f"deal ≥ $50M ({r.get('deal_value')})")
    ent = (entities or {}).get(r.get("cin") or "")
    if ent and str(ent.get("listed", "")).lower().startswith(("y", "l")):
        if level == "unknown":
            level = "medium"
        reasons.append("listed entity")
    if level == "unknown" and (r.get("role") == "Partner"):
        level = "low"
        reasons.append("Indian partner — fee bar unproven")
    return level, "; ".join(reasons) or "no backer/deal-size evidence"


def score_bd(r, ss3_signals=None, entities=None):
    """R3: composite BD Priority (0-100) with a visible factor breakdown.
    DETERMINISTIC — weights in dc_config.BD_FACTORS; role gates per the PRD:
    Noise => Exclude; Market-signal/Case-study => cap P3; all-T3 => cap P3."""
    W = dc.BD_FACTORS
    role = r.get("role") or ""
    rec = _recency_weight(r.get("last_signal", ""))

    trig = max([dc.SIGNAL_LABELS[l][0] for l, _ in _signals_for(r, ss3_signals)] or [0.0])
    if r.get("deal_value"):
        trig = max(trig, 1.0)
    if int(r.get("partnership_strength") or 0) > 0:
        trig = max(trig, dc.SIGNAL_LABELS["jv-partnership"][0])
    trig *= rec

    fit = {"Prospect": 1.0, "Partner": 0.6, "Case-study": 0.3,
           "Market-signal": 0.2, "Noise": 0.0}.get(role, 0.4)
    if (r.get("whitespace_label") or "") not in ("India market-entry", "India expansion"):
        fit *= 0.7

    access = {"Infra-investor": 0.9, "Other": 0.8, "GCC-operator": 0.7,
              "Indian-operator": 0.6, "Hyperscaler": 0.2}.get(r.get("company_type"), 0.5)

    india = _india_relevant(r)
    cross = (1.0 if (r.get("is_foreign") and india)
             else 0.9 if (r.get("company_type") == "GCC-operator" and india)
             else 0.3 if india else 0.0)

    pol = min(int(r.get("policy_tailwind") or 0), 3) / 3
    states = [s.strip() for s in (r.get("states") or "").split(";") if s.strip()]
    if states:
        try:
            import dc_states
            flags = dc_states.validity_flags()
            mx = {m["state"]: m for m in dc_states.targeting_matrix()}
            if any(mx.get(s, {}).get("priority") == "1" and s not in flags for s in states):
                pol = min(1.0, pol + 0.2)          # active P1 state, clause-safe policy base
        except Exception:
            pass

    fv, fv_why = fee_viability(r, entities)
    deal = {"high": 1.0, "medium": 0.6, "low": 0.3}.get(fv, 0.2)

    conf = _t1_share(r.get("source_tier_mix"))

    factors = {"trigger_strength": round(trig, 2), "tag_fit": round(fit, 2),
               "buyer_access": access, "cross_border": cross,
               "policy_exposure": round(pol, 2), "deal_size": deal,
               "timing": round(rec, 2), "source_confidence": round(conf, 2)}
    score = round(100 * sum(W[k] * v for k, v in factors.items()), 1)

    if role == "Noise":
        priority = "Exclude"
    else:
        priority = ("P1 Act now" if score >= dc.BD_PRIORITY_CUTOFFS["P1"]
                    else "P2 Qualify" if score >= dc.BD_PRIORITY_CUTOFFS["P2"]
                    else "P3 Monitor")
        if (role in ("Market-signal", "Case-study") or r.get("all_t3")
                or r.get("corroborated") is False):    # M5c: uncorroborated never above P3
            if priority != "P3 Monitor":
                priority = "P3 Monitor"            # PRD gates: never above P3
    breakdown = " · ".join(f"{k.replace('_', ' ')} {v:.2f}×{W[k]:.2f}→{100 * W[k] * v:.0f}"
                           for k, v in factors.items())
    return {"bd_score": score, "bd_priority": priority, "bd_factors": factors,
            "factor_breakdown": breakdown, "fee_viability": fv, "fee_viability_why": fv_why}


def _recency_weight(datestr):
    import dc_score
    return dc_score._recency(datestr) if datestr else 0.3


def _confidence(r):
    if r.get("deal_value") or int(r.get("partnership_strength") or 0) > 0:
        return "high"
    return "med" if r.get("india_presence") in ("established", "announced") else "low"


def _trigger(r, register):
    ids = [i.strip() for i in (r.get("top_evidence_ids") or "").split(",") if i.strip()]
    co = (r.get("company") or "").lower().split()[0] if r.get("company") else ""
    heads = [register[i]["headline"] for i in ids if register.get(i) and register[i].get("headline")]
    # prefer a headline that actually names the company (avoids e.g. a CEVA headline on AirTrunk)
    head = next((h for h in heads if co and co in h.lower()), heads[0] if heads else "")
    return " · ".join(p for p in (r.get("deal_value"), head[:80]) if p) or (r.get("development_type") or "activity")


def build(ranked, register):
    """-> (pipeline_rows, gcc_rows). India-relevant => pipeline; GCC-only => watch."""
    pipeline, gcc = [], []
    for r in ranked:
        if not _india_relevant(r):
            gcc.append({"company": r.get("company"), "geo": r.get("geo", ""),
                        "latest signal": r.get("last_signal", ""),
                        "note": f"GCC-only, no India signal (Signal Score {r.get('score')})"})
            continue
        ev_ids = [i.strip() for i in (r.get("top_evidence_ids") or "").split(",") if i.strip()][:4]
        ev = "; ".join(dc_evidence.label(i, register) for i in ev_ids)
        if (r.get("bd_priority") or "") == "Exclude":
            continue                                   # role=Noise never enters the BD tab
        pipeline.append({
            "Priority": r.get("bd_priority") or _priority(r), "Company": r.get("company"),
            "Segment": (r.get("layer") or "").split(";")[0].strip() or "General",
            "Trigger": _trigger(r, register),
            "Why-now": r.get("why_now") or r.get("last_signal", ""),
            "India stage": f"{r.get('india_presence', '?')}/{r.get('expansion_stage', '?')}",
            "Pain point": "", "TAG wedge": "", "Public buyer + role": "", "Intro path": "",
            "Confidence": _confidence(r), "Next action": "", "Evidence": ev,
            "Owner": "", "Status": "New",
            "Role": r.get("role", ""), "Type": r.get("company_type", ""),
            "BD Score": r.get("bd_score", ""), "Factor breakdown": r.get("factor_breakdown", ""),
            "Fee viability": (f"{r.get('fee_viability')} — {r.get('fee_viability_why')}"
                              if r.get("fee_viability") else ""),
            "Source tiers": r.get("source_tier_mix", ""),
        })
    order = {"P1 Act now": 0, "P2 Qualify": 1, "P3 Monitor": 2}
    pipeline.sort(key=lambda x: (order.get(x["Priority"], 9), -float(x.get("BD Score") or 0)))
    return pipeline, gcc


def _load_cache():
    try:
        with open(BD_CACHE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_cache(c):
    with open(BD_CACHE, "w", encoding="utf-8") as f:
        json.dump(c, f, ensure_ascii=False, separators=(",", ":"))


def ai_draft(rows, evidence_by_company):
    """Fill the soft columns with grounded, explicitly-marked AI drafts. Non-fatal + cached."""
    import dc_ai
    cache = _load_cache()
    todo = []
    for r in rows:
        co = r["Company"]
        ev = evidence_by_company.get(co, [])
        h = hashlib.sha1(("|".join(["v2", r["Trigger"], r["India stage"]] + ev)).encode("utf-8")).hexdigest()[:12]  # v2 busts cache for richer pain_point prompt
        r["_h"] = h
        if (cache.get(co) or {}).get("h") != h:
            todo.append((co, r["Trigger"], r["India stage"], ev, h))
    if todo:
        key = os.environ.get("OPENROUTER_API_KEY")
        if key and dc_ai.test_connection(key)[0]:
            user = "Draft for:\n" + "\n".join(
                json.dumps({"company": co, "trigger": tr, "stage": st, "evidence": ev[:8]},
                           ensure_ascii=False) for co, tr, st, ev, _h in todo)
            try:
                arr = dc_ai._json_array(dc_ai._chat(key, _BD_SYS, user, 3500, 0.2))
                byco = {o.get("company"): o for o in arr if isinstance(o, dict)}
                for co, tr, st, ev, h in todo:
                    o = byco.get(co)
                    if o:
                        cache[co] = {"h": h, **{k: o.get(k, "") for _c, k in _SOFT}}
                _save_cache(cache)
            except Exception as e:
                print(f"  [bd-ai] {e}")
    for r in rows:
        v = cache.get(r["Company"]) or {}
        if v.get("h") == r.get("_h"):
            for col, k in _SOFT:
                val = (v.get(k) or "").strip()
                if val:
                    r[col] = AI_MARK + val
        r.pop("_h", None)
    return rows


def write(ss, pipeline, gcc):
    import dc_sheets
    ws = dc_sheets.get_tab(ss, dc.BD_PIPELINE_TAB, BD_HEADER)
    dc_sheets._retry(ws.clear)
    grid = [BD_HEADER] + [[r.get(k, "") for k in BD_HEADER] for r in pipeline]
    dc_sheets._retry(ws.update, "A1", grid, value_input_option="USER_ENTERED")  # Evidence has HYPERLINK-free labels; USER_ENTERED harmless
    gw = dc_sheets.get_tab(ss, dc.GCC_WATCH_TAB, GCC_HEADER)
    dc_sheets._retry(gw.clear)
    ggrid = [GCC_HEADER] + [[r.get(k, "") for k in GCC_HEADER] for r in gcc]
    dc_sheets._retry(gw.update, "A1", ggrid, value_input_option="RAW")
    return len(pipeline), len(gcc)


def _selfcheck():
    reg = {"n1": {"headline": "AirTrunk $5B India DC", "publisher": "ET", "date": "2026-07-01", "url": "http://x"}}
    ranked = [
        {"company": "AirTrunk", "india_presence": "established", "expansion_stage": "scaling",
         "deal_value": "$5 billion", "geo": "India", "layer": "Build; Colo", "momentum": 6,
         "partnership_strength": 0, "score": 57, "top_evidence_ids": "n1", "why_now": "5GW plan"},
        {"company": "Khazna", "india_presence": "unknown", "expansion_stage": "monitor",
         "geo": "GCC; UAE", "layer": "Colo", "momentum": 2, "score": 20, "top_evidence_ids": ""},
        {"company": "SmallCo", "india_presence": "no_known_presence", "expansion_stage": "monitor",
         "geo": "India", "layer": "Colo", "momentum": 1, "partnership_strength": 0, "score": 12,
         "top_evidence_ids": ""},
    ]
    pipe, gcc = build(ranked, reg)
    assert [g["company"] for g in gcc] == ["Khazna"], gcc          # GCC-only routed out
    byco = {r["Company"]: r for r in pipe}
    assert byco["AirTrunk"]["Priority"] == "P1 Act now", byco["AirTrunk"]
    assert byco["SmallCo"]["Priority"] == "P3 Monitor", byco["SmallCo"]
    assert "AirTrunk $5B India DC" in byco["AirTrunk"]["Trigger"]
    assert byco["AirTrunk"]["Evidence"] == "ET — 1 Jul"
    # AI draft is non-fatal without a key (soft cols stay blank); does not touch the cache file
    os.environ.pop("OPENROUTER_API_KEY", None)
    ai_draft(pipe, {"AirTrunk": ["evidence"]})
    assert byco["AirTrunk"]["Pain point"] == "", "no key => soft cols blank"
    # R3 acceptance: AirTrunk/Blackstone outrank Sify in BD despite lower Signal Score;
    # all-T3 Brookfield caps at P3; Noise is excluded from the tab entirely.
    base = {"geo": "India", "layer": "Build", "momentum": 5, "policy_tailwind": 2,
            "last_signal": "2026-07-01", "top_evidence_ids": "n1", "states": "Maharashtra"}
    airtrunk = {**base, "company": "AirTrunk", "role": "Prospect", "company_type": "Other",
                "is_foreign": True, "india_presence": "established", "whitespace_label": "India expansion",
                "deal_value": "$5 billion", "partnership_strength": 1, "source_tier_mix": "T1:2 T2:3",
                "score": 56}
    blackstone = {**base, "company": "Blackstone", "role": "Prospect", "company_type": "Infra-investor",
                  "is_foreign": True, "india_presence": "announced", "whitespace_label": "India market-entry",
                  "deal_value": "$2 billion", "partnership_strength": 0, "source_tier_mix": "T1:1 T2:2",
                  "score": 50}
    sify = {**base, "company": "Sify", "role": "Partner", "company_type": "Indian-operator",
            "is_foreign": False, "india_presence": "established", "whitespace_label": "India expansion",
            "deal_value": "", "partnership_strength": 2, "source_tier_mix": "T1:3 T2:2", "score": 67}
    brook = {**base, "company": "Brookfield", "role": "Prospect", "company_type": "Infra-investor",
             "is_foreign": True, "india_presence": "announced", "whitespace_label": "India market-entry",
             "deal_value": "$1 billion", "all_t3": True, "source_tier_mix": "T3:4", "score": 45}
    noise = {**base, "company": "CoreWeave", "role": "Noise", "company_type": "Other",
             "is_foreign": True, "score": 30}
    for r in (airtrunk, blackstone, sify, brook, noise):
        r.update(score_bd(r))
    assert airtrunk["bd_score"] > sify["bd_score"], (airtrunk["bd_score"], sify["bd_score"])
    assert blackstone["bd_score"] > sify["bd_score"], (blackstone["bd_score"], sify["bd_score"])
    assert sify["score"] > airtrunk["score"]            # ...despite the higher Signal Score
    assert brook["bd_priority"] == "P3 Monitor", brook["bd_priority"]   # all-T3 cap
    solo = {**blackstone, "company": "SoloStory", "all_t3": False, "corroborated": False}
    solo.update(score_bd(solo))
    assert solo["bd_priority"] == "P3 Monitor", solo["bd_priority"]     # uncorroborated cap
    assert noise["bd_priority"] == "Exclude"
    assert airtrunk["fee_viability"] == "high" and "platform" in airtrunk["fee_viability_why"], airtrunk["fee_viability_why"]
    assert "trigger strength" in airtrunk["factor_breakdown"]
    pipe2, _ = build([airtrunk, noise], reg)
    assert [r["Company"] for r in pipe2] == ["AirTrunk"], [r["Company"] for r in pipe2]
    assert pipe2[0]["BD Score"] == airtrunk["bd_score"] and pipe2[0]["Role"] == "Prospect"
    print("dc_bd self-check: OK (R3 acceptance: AirTrunk/Blackstone > Sify; all-T3 capped; Noise excluded)")


if __name__ == "__main__":
    _selfcheck()
