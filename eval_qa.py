"""
eval_qa.py  —  quality gate for the Q&A retrieval loop (SiRA cognition selector).

The offline id-validity check in test_desk.py proves ids EXIST; it does not prove retrieval
got BETTER. This harness does: a fixed gold set (eval_qa.json) with expected evidence ids,
scored on first-pass Recall@K, citation precision, answer completeness, and widening passes —
and an A/B of the selector's reasoning ON vs OFF to LOCK dc_ai.SELECT_REASON by evidence.

Usage:
  1. Snapshot real data once:   DC_EVAL_FIXTURE=1 python dc_pipeline.py   (writes eval_fixture.json)
  2. Fill eval_qa.json with ~20 representative questions + expected ids (see the template).
  3. Run:   OPENROUTER_API_KEY=... python eval_qa.py
  Pure-metric self-check (no key/data needed):   python eval_qa.py --selftest
"""
import json
import os
import re
import sys

import dc_ai
import dc_state_context

FIXTURE = os.path.join(os.path.dirname(__file__), "eval_fixture.json")
GOLD = os.path.join(os.path.dirname(__file__), "eval_qa.json")


def dump_fixture(tabs, register):
    """Called by dc_pipeline.main() under DC_EVAL_FIXTURE=1 — snapshot tabs+register for eval."""
    with open(FIXTURE, "w", encoding="utf-8") as f:
        json.dump({"tabs": tabs, "register": register}, f, ensure_ascii=False)
    print(f"  [eval] fixture written: {FIXTURE}")


# --- pure metrics (unit-tested in _selftest) -------------------------------------------------
def recall_at_k(retrieved, expect):
    """|retrieved ∩ expect| / |expect|. 1.0 when nothing is expected (out-of-scope rows)."""
    exp = set(expect or [])
    if not exp:
        return 1.0
    return len(exp & set(retrieved or [])) / len(exp)


def citation_precision(cited, expect):
    """|cited ∩ expect| / |cited|. 1.0 when nothing was cited (nothing wrong asserted)."""
    cit = set(cited or [])
    if not cit:
        return 1.0
    return len(cit & set(expect or [])) / len(cit)


def completeness(answer, must_cover):
    """Fraction of must_cover phrases present in the answer (case-insensitive substring)."""
    pts = must_cover or []
    if not pts:
        return 1.0
    a = (answer or "").lower()
    return sum(1 for p in pts if p.lower() in a) / len(pts)


def _passes_count(digest):
    m = re.search(r"passes:\s*(\d+)", digest or "")
    return int(m.group(1)) if m else 0


# --- runner ---------------------------------------------------------------------------------
def _state_ctx(states, want_gaps=False):
    return "\n\n".join(c for c in
                       (dc_state_context.load_state_context(s, want_gaps) for s in states) if c)


def _run(key, gold, tabs, register):
    index = dc_ai._qa_index(tabs, register)
    known = set(register or {})
    agg = {True: [], False: []}            # first-pass recall per reasoning setting
    downstream = []                        # citation precision / completeness / widen (current SELECT_REASON)
    for row in gold:
        q = row["q"]
        states = dc_state_context.resolve_states(q)
        ctx = _state_ctx(states)
        expect = row.get("expect_ids", [])
        # A/B: first-pass recall, reasoning ON vs OFF (budget = BASE_ID_BUDGET, no widening)
        for reason in (True, False):
            picked = dc_ai.retrieve_ids(key, index, q, dc_ai.BASE_ID_BUDGET, known,
                                        state_ctx=ctx, reason=reason)
            agg[reason].append(recall_at_k(picked, expect))
        # downstream metrics via the full loop (uses dc_ai.SELECT_REASON as shipped)
        res, digest = dc_ai._answer_one(key, {"id": row.get("id", "eval"), "q": q},
                                        tabs, register, index, known)
        downstream.append({
            "q": q[:60],
            "cite_prec": citation_precision(res["evidence_ids"], expect),
            "complete": completeness(res["a"], row.get("must_cover")),
            "passes": _passes_count(digest),
            "unverified": "[UNVERIFIED:" in res["a"],   # faithfulness backstop fired
            "oos_ok": (res["a"] == dc_ai.OUT_OF_SCOPE) if not expect else None,
        })
    return agg, downstream


def _mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def main():
    if not os.path.exists(FIXTURE):
        sys.exit("no eval_fixture.json — run: DC_EVAL_FIXTURE=1 python dc_pipeline.py")
    if not os.path.exists(GOLD):
        sys.exit(f"no {GOLD} — fill the gold set first")
    key = os.environ.get("OPENROUTER_API_KEY") or sys.exit("set OPENROUTER_API_KEY")
    with open(FIXTURE, encoding="utf-8") as f:
        fx = json.load(f)
    with open(GOLD, encoding="utf-8") as f:
        gold = [g for g in json.load(f) if not str(g.get("q", "")).startswith("#")]

    agg, downstream = _run(key, gold, fx["tabs"], fx["register"])
    print(f"\n=== first-pass Recall@{dc_ai.BASE_ID_BUDGET}  (selector A/B, n={len(gold)}) ===")
    print(f"  reasoning ON : {_mean(agg[True]):.3f}")
    print(f"  reasoning OFF: {_mean(agg[False]):.3f}")
    print(f"  -> keep dc_ai.SELECT_REASON = "
          f"{'True' if _mean(agg[True]) > _mean(agg[False]) else 'False'} (higher recall)")
    print(f"\n=== downstream (SELECT_REASON={dc_ai.SELECT_REASON}) ===")
    print(f"  citation precision: {_mean([d['cite_prec'] for d in downstream]):.3f}")
    print(f"  completeness      : {_mean([d['complete'] for d in downstream]):.3f}")
    print(f"  mean widen passes : {_mean([d['passes'] for d in downstream]):.2f}")
    n_unv = sum(1 for d in downstream if d['unverified'])
    print(f"  faithfulness      : {len(downstream) - n_unv}/{len(downstream)} clean "
          f"({n_unv} had an UNVERIFIED claim scrubbed)")
    oos = [d['oos_ok'] for d in downstream if d['oos_ok'] is not None]
    if oos:
        print(f"  out-of-scope handled: {sum(oos)}/{len(oos)}")


def _selftest():
    assert recall_at_k(["a", "b"], ["a", "b", "c"]) == 2 / 3
    assert recall_at_k([], []) == 1.0                       # nothing expected -> perfect
    assert recall_at_k([], ["a"]) == 0.0
    assert citation_precision(["a", "x"], ["a", "b"]) == 0.5
    assert citation_precision([], ["a"]) == 1.0             # cited nothing -> asserted nothing wrong
    assert completeness("Gujarat CAPEX subsidy is 25%", ["capex", "25%"]) == 1.0
    assert completeness("no numbers here", ["25%"]) == 0.0
    assert _passes_count("states resolved: Gujarat   passes: 3") == 3
    print("eval_qa self-check: OK")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        _selftest()
    else:
        main()
