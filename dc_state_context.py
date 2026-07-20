"""
dc_state_context.py — state is the retrieval unit for Q&A (India State Bible).

For a question materially concerning a state, load that state's COMPLETE
state_context.md (never a tag-filtered slice — per claude_handover/02 contract).
Gujarat is bible-backed today; every other state falls back to the legacy
india_state_bank.md section via dc_states. No web retrieval ever.
"""
import os
import re

import dc_states

BIBLE_ROOT = os.path.join(os.path.dirname(__file__), "knowledge", "india_state_bible", "states")

# Rich aliases only for bible-backed states (cities/regions/authorities/licensees,
# handover 02 §2). Every other Indian state resolves by its bank name (added below).
_BIBLE_ALIASES = {
    "Gujarat": ["gujarat", "gj", "ahmedabad", "gandhinagar", "gift city", "gift",
                "dholera", "dsir", "dicdl", "dsirda", "jamnagar", "surat", "vadodara"],
}


def _alias_table():
    """alias token -> display state name. Bible aliases + every bank state by name."""
    table = {}
    for name, aliases in _BIBLE_ALIASES.items():
        for a in aliases:
            table[a] = name
    try:
        for r in dc_states.targeting_matrix():          # legacy bank states, name-only
            table.setdefault(r["state"].lower(), r["state"])
    except Exception:
        pass
    return table


def resolve_states(question):
    """-> ordered list of state display names the question concerns (may be empty)."""
    q = (question or "").lower()
    hits = []
    for alias, name in _alias_table().items():
        if re.search(rf"\b{re.escape(alias)}\b", q) and name not in hits:
            hits.append(name)
    return hits


def load_state_context(name, want_gaps=False):
    """Complete state_context.md for a bible state (+ source_gaps.md if want_gaps),
    else the legacy bank section. '' if nothing is known about the state."""
    slug = name.strip().lower().replace(" ", "-")
    ctx_path = os.path.join(BIBLE_ROOT, slug, "state_context.md")
    if os.path.exists(ctx_path):
        # ponytail: whole file loaded; add the deterministic section-preserve trim
        # (handover 02 §6) only when a state_context.md actually exceeds context budget.
        text = _read(ctx_path)
        if want_gaps:
            gaps = os.path.join(BIBLE_ROOT, slug, "source_gaps.md")
            if os.path.exists(gaps):
                text += "\n\n=== SOURCE GAPS ===\n" + _read(gaps)
        return text
    return dc_states.state_section(name)                # legacy fallback (non-bible states)


# Conditional-load predicates (handover 02 §4).
_GAP_WORDS = ("verif", "missing", "gap", "conflict", "uncertain", "diligence",
              "execution", "beyond announce", "fresh", "expir", "implement",
              "sanction", "status", "proven", "confirmed")
_DOC_WORDS = ("clause", "page ", "exact", "wording", "quote", "appendix",
              "schedule", "amendment", "provision", "sub-section", "section ")


def wants_gaps(question):
    q = (question or "").lower()
    return any(w in q for w in _GAP_WORDS)


def wants_docs(question):
    q = (question or "").lower()
    return any(w in q for w in _DOC_WORDS)


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


if __name__ == "__main__":  # tiny self-check
    assert resolve_states("Best DC company for Dholera?") == ["Gujarat"], resolve_states("Dholera")
    assert resolve_states("nothing here") == []
    assert wants_gaps("has this been verified?") and not wants_gaps("who is the CEO")
    print("dc_state_context: OK")
