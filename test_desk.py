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

print("test_desk: OK")
