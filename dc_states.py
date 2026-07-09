"""
dc_states.py  —  M6a: India state intelligence (deterministic layer).

Source of truth = knowledge/india_state_bank.md (verbatim, clause-verified, with
its S1–S47 sources table — see dc_config.STATE_BANK_PATH). This module only
PARSES and JOINS it; it never invents state facts:

- map_state(text)      city/state-name -> state (dc_config.CITY_STATE_MAP)
- state_section(state) the state's markdown section (two-pass LLM rule: only
                       MATCHED sections are ever fed to a model, never the bank)
- targeting_matrix()   the bank's State Targeting Matrix table, parsed
- validity_flags()     policy-expiry warnings computed from dates (deterministic)
- upside_states()      high policy confidence × low execution proof (Odisha-class)
- attach_states(rows)  tag evidence/prospect rows with matched states

AI boundary: states enrich prose and (in M7) the policy_exposure factor — they
never upgrade a company's role or priority.
"""
import os
import re
from datetime import date, datetime

import dc_config as dc

BANK_PATH = os.path.join(os.path.dirname(__file__), dc.STATE_BANK_PATH)

# Policy validity registry (clause dates from the bank; recheck notes travel with it).
# state -> (valid_until | None, note)
STATE_POLICY_VALIDITY = {
    "Tamil Nadu":    (date(2026, 3, 31), "2021 policy ran to 31-Mar-2026; reported lapsing — confirm renewal before pitching incentives"),
    "West Bengal":   (date(2026, 9, 6),  "2021 policy notified 06-09-2021 for five years — replacement/extension check before Sep-2026 use"),
    "Karnataka":     (date(2027, 5, 7),  "2022-27 policy in force from 07-05-2022"),
    "Haryana":       (date(2031, 5, 27), "2026 policy five years from 27-05-2026 gazette; OCR clause-usable, final legal check advised"),
    "Uttar Pradesh": (None, "2026 policy cabinet-approved 06-07-2026 — official GO/PDF still needed for clause-level use"),
}


def _read_bank():
    with open(BANK_PATH, encoding="utf-8") as f:
        return f.read()


def bank_checked_date():
    m = re.search(r"^Checked:\s*(\d{4}-\d{2}-\d{2})", _read_bank(), re.M)
    return datetime.strptime(m.group(1), "%Y-%m-%d").date() if m else None


def bank_freshness_warning(max_days=None):
    """Non-fatal staleness signal: '' when fresh, else a warning line."""
    max_days = max_days or dc.STATE_BANK_STALE_DAYS
    d = bank_checked_date()
    if not d:
        return "state bank has no 'Checked:' date"
    age = (date.today() - d).days
    return f"state bank is {age}d old (checked {d}) — recheck clauses" if age > max_days else ""


def state_names():
    return sorted({s for s in dc.CITY_STATE_MAP.values()} | set(STATE_POLICY_VALIDITY))


def map_state(text):
    """All states named (directly or via a city) in `text`. Deterministic."""
    low = f" {(text or '').lower()} "
    found = set()
    for city, state in dc.CITY_STATE_MAP.items():
        if city in low:
            found.add(state)
    for state in state_names():
        if state.lower() in low:
            found.add(state)
    return sorted(found)


def state_section(state):
    """The bank's `### <State>` section, verbatim (empty string if absent)."""
    text = _read_bank()
    m = re.search(rf"^### {re.escape(state)}\s*$(.*?)(?=^#{{2,3}} |\Z)", text, re.M | re.S)
    return f"### {state}\n{m.group(1).strip()}" if m else ""


def targeting_matrix():
    """Parse the '## State Targeting Matrix' table -> [{state, priority, pitch,
    policy_confidence, execution_confidence, gap}]. The bank table is the truth."""
    text = _read_bank()
    m = re.search(r"^## State Targeting Matrix\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    rows = []
    if not m:
        return rows
    for line in m.group(1).splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 6 or cells[0] in ("State", "") or set(cells[0]) <= {"-", ":", " "}:
            continue
        rows.append({"state": cells[0], "priority": cells[1], "pitch": cells[2],
                     "policy_confidence": cells[3], "execution_confidence": cells[4],
                     "gap": cells[5]})
    return rows


def validity_flags(today=None):
    """{state: warning} for expired / soon-expiring / unverified policy bases."""
    today = today or date.today()
    flags = {}
    for state, (until, note) in STATE_POLICY_VALIDITY.items():
        if until is None:
            flags[state] = f"⚠ {note}"
        elif until < today:
            flags[state] = f"⚠ policy EXPIRED {until} — {note}"
        elif (until - today).days <= 90:
            flags[state] = f"⚠ policy expires {until} — {note}"
    return flags


def upside_states():
    """Deterministic whitespace: policy confidence High but execution below Medium
    (the Odisha pattern — generous verified policy, thin hyperscale execution)."""
    out = []
    for r in targeting_matrix():
        pol = r["policy_confidence"].lower()
        exe = r["execution_confidence"].lower()
        if pol.startswith("high") and ("low" in exe or exe.startswith("medium-low")):
            out.append(r["state"])
    return out


def attach_states(rows, text_keys=("geo", "title", "summary", "excerpt", "actor")):
    """Tag each row with `states` = '; '-joined matches over its text fields."""
    for r in rows:
        blob = " ".join(str(r.get(k) or "") for k in text_keys)
        st = map_state(blob)
        if st:
            r["states"] = "; ".join(st)
    return rows


def signal_counts(tabs):
    """{state: live signal count} over SS1/SS2 rows (title+geo text match)."""
    counts = {}
    for r in (tabs.get("ss1") or []) + (tabs.get("ss2") or []):
        for s in map_state(f"{r.get('geo', '')} {r.get('title', '')}"):
            counts[s] = counts.get(s, 0) + 1
    return counts


DILIGENCE_TASKS = [
    "Pull the official UP Data Centre Policy 2026 GO/policy PDF (cabinet-approved only)",
    "Final legal review of Haryana 2026 OCR against the original Gazette PDF",
    "Confirm Tamil Nadu 2021 policy renewal/replacement/lapse after 31-Mar-2026",
    "Official pages for HP State Data Hosting Policy + Uttarakhand AI Mission-2025",
    "Check AP for a broader DC incentive policy beyond the DDL power framework",
    "Pull the KDEM/Silicon Beach/Deloitte Mangaluru feasibility report",
    "Add primary/company sources for every case-study card",
]


def export_payload(tabs=None):
    """The dashboard `states` slice: matrix + flags + upside + live counts."""
    flags = validity_flags()
    counts = signal_counts(tabs or {})
    return {"checked": str(bank_checked_date() or ""),
            "freshness_warning": bank_freshness_warning() or None,
            "upside": upside_states(),
            "diligence": DILIGENCE_TASKS,
            "matrix": [{**r, "validity_flag": flags.get(r["state"]),
                        "live_signals": counts.get(r["state"], 0)}
                       for r in targeting_matrix()]}


def write_tab(sheet, tabs):
    """M6c: the 'State Targeting' sheet tab (clear+rebuild, non-fatal caller)."""
    import dc_sheets
    header = ["state", "priority", "core pitch", "policy confidence",
              "execution confidence", "main gap", "validity flag", "live signals"]
    p = export_payload(tabs)
    grid = [[f"STATE TARGETING — India DC state bank (checked {p['checked']})"
             + (f" · {p['freshness_warning']}" if p['freshness_warning'] else "")],
            [f"Upside states (high policy × thin execution): {', '.join(p['upside']) or '—'}"],
            [""], header]
    for r in p["matrix"]:
        grid.append([r["state"], r["priority"], r["pitch"], r["policy_confidence"],
                     r["execution_confidence"], r["gap"], r.get("validity_flag") or "",
                     r["live_signals"]])
    grid += [[""], ["IMMEDIATE DILIGENCE TASKS (from the bank)"]] + [[t] for t in p["diligence"]]
    ws = dc_sheets.get_tab(sheet, dc.STATE_TARGETING_TAB, header)
    dc_sheets._retry(ws.clear)
    dc_sheets._retry(ws.update, "A1", grid, value_input_option="RAW")
    return len(p["matrix"])


def _selfcheck():
    # city mapping
    assert map_state("AirTrunk plans Navi Mumbai hyperscale campus") == ["Maharashtra"]
    assert "Andhra Pradesh" in map_state("Google's Vizag AI hub with Adani")
    assert map_state("STT launches fourth Siruseri data centre") == ["Tamil Nadu"]
    assert "Uttar Pradesh" in map_state("Yotta Greater Noida expansion")
    # every first/second-wave state has a parseable section
    for s in ("Maharashtra", "Uttar Pradesh", "Telangana", "Tamil Nadu", "Andhra Pradesh",
              "Odisha", "Gujarat", "West Bengal", "Karnataka", "Haryana"):
        sec = state_section(s)
        assert sec.startswith(f"### {s}") and len(sec) > 400, (s, len(sec))
    # matrix parses all 12 states
    mx = targeting_matrix()
    assert len(mx) == 12, len(mx)
    assert {r["state"] for r in mx} >= {"Maharashtra", "Odisha", "Haryana", "Uttarakhand"}
    # validity flags fire (TN lapsed; WB inside 90d as of the bank's check date)
    fl = validity_flags(today=date(2026, 7, 8))
    assert "EXPIRED" in fl.get("Tamil Nadu", ""), fl.get("Tamil Nadu")
    assert "expires" in fl.get("West Bengal", ""), fl.get("West Bengal")
    # Odisha is the canonical upside state
    ups = upside_states()
    assert "Odisha" in ups, ups
    # attach_states tags evidence rows
    rows = attach_states([{"geo": "India", "title": "Dholera green AI campus MoU"}])
    assert rows[0]["states"] == "Gujarat", rows
    # freshness signal exists and is well-formed
    assert bank_checked_date() is not None
    p = export_payload({"ss1": [{"geo": "India", "title": "Vizag AI hub news"}]})
    assert len(p["matrix"]) == 12 and p["upside"] == ["Odisha"]
    ap = next(r for r in p["matrix"] if r["state"] == "Andhra Pradesh")
    assert ap["live_signals"] == 1, ap
    print(f"dc_states self-check: OK (12 states, upside={ups}, "
          f"{len(validity_flags())} validity flags today)")


if __name__ == "__main__":
    _selfcheck()
