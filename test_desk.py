"""Analyst Desk self-check: eligibility, window widening, validation, date math,
evidence pinning. Run: python test_desk.py  (no framework, asserts only)."""
from datetime import date, timedelta

import dc_ai

TODAY = date(2026, 7, 17)
D = lambda n: (TODAY - timedelta(days=n)).isoformat()

TABS = {"ss1": [{"id": "n-fresh"}, {"id": "n-old"}],
        "ss2": [{"id": "p-mid"}],
        "ss3": [{"accession": "f-fresh"}],
        "ss4": [{"id": "o-week"}]}
REG = {"n-fresh": {"date": D(1)}, "n-old": {"date": D(40)},
       "p-mid": {"date": D(3)}, "f-fresh": {"date": D(1)}, "o-week": {"date": D(6)}}

def mover(co, ids, role=""):
    return {"company": co, "role": role, "top_evidence_ids": ",".join(ids),
            "india_presence": "established", "score": 50, "signal_band": "Moderate"}

# --- eligibility + window widening -------------------------------------------------
# A: 2 streams, fresh (1d)   B: 2 streams, 6d   C: 1 stream only   D: banned role
computed = {"movers": [
    mover("A", ["n-fresh", "f-fresh"]),
    mover("B", ["p-mid", "o-week"]),          # freshest 3d -> in 4d window
    mover("C", ["n-fresh"]),                  # single stream -> never eligible
    mover("D", ["n-fresh", "f-fresh"], role="Market-signal"),
]}
w, cands = dc_ai._tri_candidates(computed, REG, TABS, today=TODAY)
names = {c["p"]["company"] for c in cands}
assert "C" not in names and "D" not in names, names
assert "A" in names, names
# only A is within 2d; widening stops at 4d where B joins (still <3 -> widens to 14)
assert w == 14 and names == {"A", "B"}, (w, names)

# --- validation: hallucinated ids, wrong company, code-side dates ------------------
obj = {"top_plays": [
    {"company": "A", "headline": "H" * 300, "why_now": "because", "streams": ["osint"],
     "evidence_ids": ["n-fresh", "GHOST", "f-fresh"], "state_hook": "x", "confidence": "medium"},
    {"company": "NotACandidate", "evidence_ids": ["n-fresh"]},
    {"company": "B", "evidence_ids": ["GHOST-ONLY"]},
], "watchlist": [{"company": "B", "note": "watch"}, {"company": "Nope", "note": "x"}]}
tri = dc_ai._validate_tri(obj, cands, REG, w, TABS, today=TODAY)
assert len(tri["top_plays"]) == 1, tri                      # ghost-only + non-candidate dropped
pl = tri["top_plays"][0]
assert pl["evidence_ids"] == ["n-fresh", "f-fresh"]         # GHOST removed
assert pl["streams"] == ["filings", "news"]                 # derived from ids, not model
assert pl["freshest_signal"] == D(1)                        # computed, not model-claimed
assert pl["act_by"] == (TODAY - timedelta(days=1) + timedelta(days=30)).isoformat()
assert pl["expired"] is False and pl["confidence"] == "med" and len(pl["headline"]) == 160
assert [w_["company"] for w_ in tri["watchlist"]] == ["B"]  # non-candidate dropped

# expired flag
old_reg = {"n-fresh": {"date": D(45)}, "f-fresh": {"date": D(45)}}
cands2 = [{"p": mover("A", ["n-fresh", "f-fresh"]), "ids": [], "streams": set(), "fresh": None}]
tri2 = dc_ai._validate_tri({"top_plays": [{"company": "A", "evidence_ids": ["n-fresh"]}]},
                           cands2, old_reg, 14, TABS, today=TODAY)
assert tri2["top_plays"][0]["expired"] is True

# --- exporter pins cited evidence under the register cap ---------------------------
import dc_export
orig_cap = dc_export.CAP_EVIDENCE
try:
    dc_export.CAP_EVIDENCE = 1
    tabs_x, computed_x, register_x, pipe, gcc, md, health = dc_export._fixture_bundle()
    tri_x = {"status": "ok", "generated_at": "t", "window_days_used": 2,
             "top_plays": [{"company": "AirTrunk", "headline": "h", "why_now": "w",
                            "streams": ["news"], "evidence_ids": ["n2"], "state_hook": "s",
                            "freshest_signal": "2026-07-06", "act_by": "2026-08-05",
                            "expired": False, "confidence": "med"}], "watchlist": []}
    data = dc_export.build(tabs_x, computed_x, register_x, pipe, gcc, md,
                           triangulation=tri_x, qa=[], health=health)
    assert list(data["evidence_register"]) == ["n2"], data["evidence_register"].keys()
finally:
    dc_export.CAP_EVIDENCE = orig_cap

# --- Q&A: state resolution, selector validation, multi-pass widen cap, backfill -----
import dc_state_context

# state detection maps a city/region alias to the state; unrelated text -> nothing
assert dc_state_context.resolve_states("best DC company for Dholera?") == ["Gujarat"]
assert dc_state_context.resolve_states("who is the CEO") == []
assert dc_state_context.wants_gaps("has this been verified?")
# bible load returns the whole doc incl. §19 when present; else falls back cleanly
gj = dc_state_context.load_state_context("Gujarat")
assert gj == "" or "Investment and Business-Development Judgment" in gj, "bible load"

# selector output validation drops hallucinated ids
assert dc_ai._clean_ids(["n-fresh", "GHOST", "n-fresh"], {"n-fresh", "p-mid"}) == ["n-fresh"]

# state-context cite verification: §21 map parses, valid cites kept+described, fakes dropped
_smap = dc_state_context.source_map(
    "- `GJ-POL-2026-001` — official Viksit Gujarat Data Center Policy booklet.\n"
    "- `GJ-POW-2023-001` — Gujarat Renewable Energy Policy 2023.")
assert _smap["GJ-POL-2026-001"].startswith("official Viksit"), _smap
_cites = dc_ai._state_cites(
    "Clears the threshold [GJ-POL-2026-001, p.13], again [GJ-POL-2026-001], user src [GJ-POW-2023-001], not [GJ-FAKE-9999-001].",
    _smap, {"GJ-POL-2026-001": {"url": "https://example.gov/policy.pdf", "provider": False},
            "GJ-POW-2023-001": {"url": "", "provider": True}})
assert [c["id"] for c in _cites] == ["GJ-POL-2026-001", "GJ-POW-2023-001"], _cites   # deduped, fake dropped
assert _cites[0]["url"] == "https://example.gov/policy.pdf" and _cites[0]["provider"] is False
assert _cites[1]["url"] == "" and _cites[1]["provider"] is True   # user-supplied -> provider flag

# multi-pass loop: stub the model so the judge never accepts -> must stop at MAX_PASSES
QTABS = {"ss1": [{"id": "n-fresh", "title": "T", "summary": "S"}], "ss2": [], "ss3": [], "ss4": []}
QREG = {"n-fresh": {"company": "A", "date": D(1), "headline": "h"}}
calls = {"answer": 0}
def _fake_chat(key, system, user, max_tokens, temperature=0.2, reason=False):
    if system is dc_ai.RETRIEVE_SYSTEM:
        return '{"ids":["n-fresh","GHOST"]}'
    if system is dc_ai.ANSWER_SYSTEM:
        calls["answer"] += 1
        return '{"a":"weak draft","evidence_ids":["n-fresh"]}'
    if system is dc_ai.JUDGE_SYSTEM:
        return '{"usable":false,"missing":["more evidence"]}'
    return "{}"
_real_chat = dc_ai._chat
try:
    dc_ai._chat = _fake_chat
    ans = dc_ai.answer_questions("k", QTABS, {"movers": []}, QREG,
                                 [{"id": "q-1", "q": "tell me about A in Gujarat"}])
    assert calls["answer"] == dc_ai.MAX_PASSES, calls           # widened to the cap, not forever
    assert ans["q-1"]["evidence_ids"] == ["n-fresh"], ans       # ghost dropped, real id kept
    # a question the model omits entirely still gets a backfilled answer (never re-queues silent)
    dc_ai._chat = lambda *a, **k: "{}"
    ans2 = dc_ai.answer_questions("k", QTABS, {"movers": []}, QREG, [{"id": "q-9", "q": "x in Gujarat"}])
    assert ans2["q-9"]["a"] == dc_ai.OUT_OF_SCOPE, ans2
finally:
    dc_ai._chat = _real_chat

print("test_desk: OK")
