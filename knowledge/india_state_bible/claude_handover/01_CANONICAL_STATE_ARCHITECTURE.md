# Canonical State Architecture

## 1. Universal state directory

Every state and union territory must use this exact top-level structure:

```text
states/<state-slug>/
├── state_context.md
├── source_gaps.md
├── research_queue.xlsx
├── change_log.xlsx
└── source_library/
    ├── source_register.xlsx
    └── documents/
```

No state may invent a different root layout. Optional subdirectories inside `source_library/documents/` may preserve legacy notes or organise files for humans, but software must use the `local_file_path` in `source_register.xlsx`, not infer subject matter from folders.

## 2. File responsibilities

### `state_context.md`

The single comprehensive state briefing supplied to the LLM for any question materially concerning that state. It contains current rules, historical lineage, incentives, infrastructure, approvals, projects, companies, execution evidence, risks, conflicts and investment judgment.

It is not a short executive summary. It should contain enough context to prevent an LLM from answering a narrow question incorrectly because a relevant caveat lived in a different tagged fragment.

### `source_gaps.md`

The human- and LLM-readable consolidated register of evidence that is missing, incomplete, conflicted, stale, inaccessible or available only in a non-authoritative form. It explains why each gap matters, what is already known and what would resolve it.

### `research_queue.xlsx`

The operational task list. Each row is a bounded research action with a target outcome, priority, proposed source path, status, attempts and results. It is not an essay and does not duplicate the full gap analysis.

### `change_log.xlsx`

The permanent record of substantive changes, corrections, source replacements, supersessions, architecture migrations and user approvals. Old positions remain intelligible.

### `source_library/source_register.xlsx`

One row per source record. It controls identity, provenance, authority, dates, completeness, local path, URL, checksum, source limitations and contextual contribution. It does not atomise the source into claim rows.

### `source_library/documents/`

The complete retained source files: policies, government resolutions, regulatory orders, company releases, filings, official pages, transcripts, datasets and archived research aids. A source file must be preserved as received wherever practical.

## 3. `state_context.md` front matter

Use these exact keys:

```yaml
---
schema_version: "1.0"
state_name: "Gujarat"
state_code: "GJ"
document_status: "working"
last_substantive_update: "2026-07-20"
information_cutoff: "2026-07-20"
---
```

These fields control document processing only. They are not content tags and must not replace the narrative.

## 4. Exact universal headings

Every heading below must exist in every state and appear in this order:

```markdown
# [State] Data Centre Context

## 00. How to Use This Document
## 01. Executive State Context
## 02. State Geography and Economic Context
## 03. Existing Data Centre Ecosystem
## 04. Policy, Law and Regulatory Lineage
## 05. Definitions and Project Eligibility
## 06. Incentives and Government Support
## 07. Power and Energy
## 08. Land, Planning and Buildings
## 09. Approvals and Compliance Path
## 10. Water, Environment and Physical Risk
## 11. Connectivity and Digital Infrastructure
## 12. Demand, Customers, Talent and Operating Economics
## 13. Companies and Data Centre Value Chain
## 14. Projects and Case Studies
## 15. Government, Political Economy and Policy Continuity
## 16. Execution Record and Delivery Capacity
## 17. Risks, Conflicts and Unresolved Questions
## 18. Location-by-Location Assessment
## 19. Investment and Business-Development Judgment
## 20. State-Specific Additional Context
## 21. Source Reference Map
```

## 5. Required internal order within a section

Where applicable, write each subject in this order:

1. Current operative position.
2. Scope and eligibility.
3. Quantitative terms.
4. Process and responsible authority.
5. Conditions, exclusions and dependencies.
6. Historical lineage or superseded position.
7. Execution evidence.
8. Material uncertainty or conflict.
9. Source citations.

This order is especially important for policy, incentives, power tariffs and projects. It prevents an older rule from appearing to be current merely because it appears first.

## 6. Missing information

Never omit a mandatory subject. Use this form:

> Not established from the sources reviewed as of YYYY-MM-DD.

Then explain what was checked and what record would resolve the question. A website search returning no result is a dated discovery limitation, not proof that the record does not exist.

## 7. Citation convention

Use the permanent source ID at the point of use:

```text
[GJ-POL-2026-001, p. 13, cl. 7.6]
[GJ-POW-2026-006, tariff schedule, pp. 48–52]
[GJ-PROJ-2026-003, article body quoting Gujarat government statement]
```

Rules:

- Cite the narrowest useful page, clause, table or page section.
- A factual paragraph may cite multiple sources.
- Company claims must be described as company claims unless independently verified.
- A launch press release cannot substitute for the operative policy.
- A policy entitlement cannot substitute for a project sanction.
- City-wide infrastructure cannot substitute for plot- or project-specific allocation.
- The source reference map gives a compact source description; the workbook holds full metadata.

## 8. Project-stage vocabulary

Use the highest stage that evidence actually proves:

```text
Announced
MoU signed
Feasibility / pre-development
Site controlled
Grid and water reserved
Materially permitted
Incentive approved
Under construction
Energised / commissioned
Operational
Incentive disbursed
Delayed / lapsed / cancelled
```

A project may have several dimensions at different stages. Record the overall stage conservatively and then state dimension-level evidence. A target commercial-operation date does not elevate stage.

## 9. Source IDs

Existing IDs such as `GJ-POL-2026-001` and `GJ-POW-2026-006` are permanent and must not be renamed because citations already depend on them. Their embedded category is legacy metadata, not a retrieval instruction.

Use category-neutral IDs for newly added sources:

```text
<STATE-CODE>-SRC-<YEAR>-<SEQUENCE>
```

Example: `GJ-SRC-2026-001`.

The source register, not the ID or folder, determines source type and coverage.

## 10. State-specific material

Section 20 exists because a universal taxonomy cannot anticipate every jurisdiction. Unique governance models, special regions, industrial corridors, political arrangements or infrastructure dependencies belong there. Custom level-three headings are permitted inside Section 20. They may not replace coverage in the universal sections.

