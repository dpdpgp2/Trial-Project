# Migration and Preservation Rules

## 1. Non-deletion rule

No content may be silently discarded during migration. Existing Gujarat research notes may be consolidated into canonical files, but the original files must be preserved under `source_library/documents/legacy_research_notes/` with their contents unchanged.

The special rule for `knowledge/india_state_bank.md` is stricter: do not edit, replace or delete any Gujarat text in that file without explicit user approval of a proposed redline. This architecture migration does not touch the bank.

## 2. Evidence migration

The former subject folders under `states/gujarat/evidence/` are too category-specific for the approved design. Move all physical evidence files into `states/gujarat/source_library/documents/` while preserving filenames and bytes.

After moving:

1. update every `local_file_path` in the source register;
2. recompute or verify SHA-256 against the legacy manifest;
3. check for duplicate IDs and duplicate filenames;
4. retain official and unofficial versions when they serve version-comparison purposes; and
5. do not infer retrieval logic from the old category prefix or directory.

## 3. Legacy authored files

Preserve these Gujarat files as immutable migration inputs:

```text
DEEP_RESEARCH_REPORT_3_AUDIT_2026-07-20.md
LT_VYOMA_DHOLERA_SOURCE_AUDIT_2026-07-19.md
PROJECT_SPECIFIC_SOURCE_REQUEST_CHECKLIST.md
SOURCE_INTAKE_2026-07-19.md
SOURCE_INTAKE_2026-07-20.md
evidence_manifest.csv
```

Move the listed Markdown files to `source_library/documents/legacy_research_notes/`. Preserve the CSV as `source_library/documents/legacy_research_notes/evidence_manifest_legacy.csv`. The former root `SOURCE_GAPS.md` is consolidated into the canonical `source_gaps.md`; on the default case-insensitive macOS filesystem those names cannot coexist as separate live files. A canonical migration snapshot may be retained with the legacy notes, while the detailed legacy request material remains independently preserved in `PROJECT_SPECIFIC_SOURCE_REQUEST_CHECKLIST.md`. The canonical files become the active interface; legacy notes remain auditable source material.

## 4. Content-mapping rules

- Policy clauses, infrastructure facts, project findings and analytical judgments go into the relevant `state_context.md` sections.
- Missing records and dated negative searches go into `source_gaps.md`, with material caveats also stated inline in `state_context.md`.
- Concrete next actions go into `research_queue.xlsx`.
- Corrections, supersessions, user rulings and the path migration go into `change_log.xlsx`.
- Source identity and provenance go into `source_register.xlsx`.

Do not copy the entire project request checklist into every file. Preserve it as a legacy note, summarise decisive gaps in `source_gaps.md`, and turn current next actions into queue rows.

## 5. Legacy source IDs

Do not rename existing IDs. Existing categories embedded in IDs are historical and may continue to appear in citations. For new records use category-neutral `STATE-SRC-YEAR-NNN` IDs.

## 6. Historical and superseded positions

When a new policy supersedes an earlier analytical conclusion:

1. state the current rule first;
2. preserve the earlier position in the policy lineage;
3. label it historical or superseded;
4. cite both the old and new sources where relevant; and
5. record the correction in `change_log.xlsx`.

For Gujarat, the earlier conclusion that the state had no standalone data-centre policy became obsolete after the 9 July 2026 launch of the dedicated policy. It must survive only as a dated historical position.

## 7. Project-stage migration

Do not convert announcements into execution during consolidation. For L&T Vyoma/Dholera, the migration status is `MoU signed / feasibility or pre-development`. No project-specific proof of site control, grid reservation, water allocation, material approvals, incentive sanction, financing, construction or commissioning had been publicly verified by 20 July 2026.

## 8. QA

Before declaring migration complete:

- compare physical-file counts before and after;
- compare SHA-256 values with the legacy manifest;
- validate all source-register paths;
- confirm all 22 state-context headings (`00` through `21`) exist once and in order;
- confirm each active gap has a queue action or an explicit reason none is useful;
- render and inspect every workbook;
- scan workbook formulas for errors;
- search for stale `evidence/` paths;
- search for conflicting references to the legacy architecture; and
- verify `india_state_bank.md` checksum is unchanged.
