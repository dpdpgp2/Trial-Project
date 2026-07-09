"""
dc_md.py  —  MD View (R6): a curated, BALANCED top-10 a TAG partner can act on.
Selector guarantees a portfolio mix across type-groups (foreign investor/operator,
GCC-to-India, Indian partner) with anchor market-signals as context rows — never
all one type, never padded with Noise. AirTrunk+Blackstone render as ONE clustered
row (dc_config.CLUSTER_ACCOUNTS); Meta/Amazon render as case-study/anchor notes
(CASE_STUDY_NOTES). Soft columns are 🤖AI-draft (from the BD Pipeline drafts).
"""
import dc_config as dc
import dc_evidence

MD_HEADER = ["Priority", "Account", "Type", "Trigger", "TAG wedge", "Buyer",
             "Access path", "Next action"]
_AI_MARK = "🤖AI-draft: "

_GROUPS = {   # type-group buckets the balance rule draws from, in order
    "foreign": ("Infra-investor", "Other"),
    "gcc": ("GCC-operator",),
    "partner": ("Indian-operator",),
}


def _group_of(r):
    for g, types in _GROUPS.items():
        if r.get("Type") in types:
            return g
    return "other"


def _cluster(rows):
    """Merge CLUSTER_ACCOUNTS pairs into one row (platform + sponsor)."""
    byco = {r["Company"]: r for r in rows}
    merged, dropped = [], set()
    for lead, spec in dc.CLUSTER_ACCOUNTS.items():
        other = spec.get("with")
        if lead in byco and other in byco:
            a, b = byco[lead], byco[other]
            keep = a if float(a.get("BD Score") or 0) >= float(b.get("BD Score") or 0) else b
            row = dict(keep)
            row["Company"] = spec.get("label", f"{lead} + {other}")
            row["Trigger"] = "; ".join(x for x in {a.get("Trigger", ""), b.get("Trigger", "")} if x)[:120]
            merged.append(row)
            dropped.update((lead, other))
    return merged + [r for r in rows if r["Company"] not in dropped]


def build(pipe, link_by_company=None, register=None):
    """BD Pipeline rows (P1/P2, already role-gated + bd-scored) -> ≤10 balanced
    MD rows + case-study/anchor notes. Degrades to fewer rows, never pads."""
    cands = [r for r in pipe if str(r.get("Priority", "")).startswith(("P1", "P2"))
             and r.get("Role") in ("Prospect", "Partner")]
    cands = _cluster(cands)
    cands.sort(key=lambda r: -float(r.get("BD Score") or 0))

    picked, seen_groups = [], set()
    for r in cands:                                   # pass 1: best of each group
        g = _group_of(r)
        if g not in seen_groups:
            picked.append(r)
            seen_groups.add(g)
    for r in cands:                                   # pass 2: fill by bd_score
        if r not in picked and len(picked) < 8:
            picked.append(r)
    picked = picked[:8]

    def soft(r, col):
        return (r.get(col) or "").replace(_AI_MARK, "")

    rows = []
    for r in picked:
        rows.append([r.get("Priority", ""), r.get("Company", ""), r.get("Type", ""),
                     (r.get("Trigger", "") or "")[:90],
                     soft(r, "TAG wedge") or r.get("India stage", ""),
                     _AI_MARK + soft(r, "Public buyer + role") if soft(r, "Public buyer + role") else "",
                     _AI_MARK + soft(r, "Intro path") if soft(r, "Intro path") else "",
                     _AI_MARK + soft(r, "Next action") if soft(r, "Next action") else ""])
    for co, note in dc.CASE_STUDY_NOTES.items():      # anchors/case-studies: context, not pitches
        if len(rows) >= 10:
            break
        rows.append(["—", co, "Market-signal", note[:90], "context only — not a prospect",
                     "", "", ""])
    return rows[:10]


def write(ss, rows, header_line):
    import dc_sheets
    ws = dc_sheets.get_tab(ss, dc.MD_VIEW_TAB, MD_HEADER)
    dc_sheets._retry(ws.clear)
    grid = [[header_line], [""], [MD_HEADER[0]] + MD_HEADER[1:]] + rows
    dc_sheets._retry(ws.update, "A1", grid, value_input_option="USER_ENTERED")
    return len(rows)


def _selfcheck():
    def bd(co, typ, role, score, prio="P1 Act now", **kw):
        r = {"Priority": prio, "Company": co, "Type": typ, "Role": role, "BD Score": score,
             "Trigger": f"{co} trigger", "India stage": "announced/entry",
             "TAG wedge": "🤖AI-draft: state land+power", "Public buyer + role": "🤖AI-draft: MahaIT",
             "Intro path": "🤖AI-draft: via sponsor", "Next action": "🤖AI-draft: brief"}
        r.update(kw)
        return r
    pipe = [bd("AirTrunk", "Other", "Prospect", 78), bd("Blackstone", "Infra-investor", "Prospect", 74),
            bd("Khazna", "GCC-operator", "Prospect", 55, prio="P2 Qualify"),
            bd("Sify", "Indian-operator", "Partner", 52, prio="P2 Qualify"),
            bd("Vantage", "Other", "Prospect", 60, prio="P2 Qualify"),
            bd("CoreWeave", "Other", "Noise", 10, prio="P3 Monitor")]
    rows = build(pipe)
    accounts = [r[1] for r in rows]
    assert "AirTrunk + Blackstone (platform + sponsor)" in accounts, accounts   # clustered
    assert "Blackstone" not in accounts and "AirTrunk" not in accounts
    assert "Khazna" in accounts and "Sify" in accounts                          # balanced mix
    assert "CoreWeave" not in accounts                                          # Noise never padded
    assert any(a == "Meta" for a in accounts) and any(a == "Amazon" for a in accounts)  # notes
    assert len(rows) <= 10
    md_row = next(r for r in rows if "AirTrunk" in r[1])
    assert md_row[5].startswith("🤖AI-draft: "), md_row                          # Buyer marked
    # degrade: thin supply -> fewer rows, no padding beyond notes
    thin = build([bd("Sify", "Indian-operator", "Partner", 52, prio="P2 Qualify")])
    assert [r[1] for r in thin][0] == "Sify" and len(thin) <= 3, thin
    print("dc_md self-check: OK (balanced ≤10, cluster merged, Noise never padded)")


if __name__ == "__main__":
    _selfcheck()
