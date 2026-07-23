# Control File Schemas

## 1. `source_library/source_register.xlsx`

Workbook purpose: permanent source inventory and provenance control. Use one worksheet named `Sources` and one row per source record.

Required columns, in order:

```text
source_id
title
short_description
issuing_body_or_author
publisher
source_type
authority_level
official_or_secondary
publication_date
notification_date
effective_date
expiry_date
access_date
current_status
supersedes
superseded_by
geographic_scope
topics_covered
projects_or_companies_covered
original_url
archive_url
local_file_path
file_format
language
page_count
document_complete
text_searchable
ocr_status
translation_status
checksum_sha256
authentication_notes
reliability_notes
important_pages_or_clauses
context_contribution
limitations
```

Rules:

- `source_id` is immutable.
- `local_file_path` is relative to the state directory.
- Dates are real spreadsheet dates where known and ISO-formatted.
- `current_status` records current, historical, superseded, time-limited, discovery-only, excluded or another clearly defined status.
- `topics_covered` assists navigation only.
- `context_contribution` explains what the source adds to the state picture.
- `limitations` says what the source cannot establish.
- One ID may map to multiple physical representations when necessary; list secondary paths in `archive_url` or the notes rather than duplicating the row.

## 2. `research_queue.xlsx`

Workbook purpose: actionable research management. Use one worksheet named `Research Queue`.

Required columns:

```text
task_id
research_question
related_gap_ids
objective
recommended_search_path
target_documents_or_authorities
next_action
priority
status
assigned_to
date_added
last_attempted
result
sources_added
follow_up_required
```

Controlled values:

- Priority: `Critical`, `High`, `Medium`, `Low`.
- Status: `Not started`, `In progress`, `Waiting for source`, `Blocked`, `Complete`, `Superseded`.
- Follow-up required: `Yes`, `No`.

One row is a bounded task, not a broad research theme. A completed task can still have an unresolved result; record the dated negative finding and create a future refresh task if appropriate.

## 3. `change_log.xlsx`

Workbook purpose: corrections, supersessions, migrations and approvals. Use one worksheet named `Change Log`.

Required columns:

```text
change_id
change_date
affected_file_or_source_id
change_type
previous_position
new_position
reason
supporting_source_ids
changed_by
approval_required
approval_status
notes
```

Controlled values:

- Change type: `Addition`, `Correction`, `Supersession`, `Path migration`, `Schema migration`, `Status update`, `User ruling`.
- Approval required: `Yes`, `No`.
- Approval status: `Not required`, `Pending`, `Approved`, `Rejected`.

Never erase the previous position from the log. If a change concerns `india_state_bank.md`, approval is always required and the bank remains untouched until approval is recorded.

## 4. `source_gaps.md`

Use this fixed structure:

```markdown
# [State] Source Gaps

## Document Control
## How to Read This Register
## Critical Gaps
## Policy and Implementation Gaps
## Project-Specific Execution Gaps
## Infrastructure and Approval Gaps
## Market, Company and Operating-Evidence Gaps
## Source-Usability and Conflict Gaps
## Dated Negative Findings
## Closed or Partially Closed Gaps
## User-Provided Source Requests
```

Each active gap must contain:

```markdown
### <GAP-ID> — <short title>

- Status:
- Priority:
- Affected context sections:
- Current understanding:
- Evidence already held:
- Missing evidence:
- Why it matters:
- Best next source:
- Last checked:
```

## 5. Identifiers

Use:

```text
Gap:     <STATE>-GAP-<NNN>
Task:    <STATE>-RQ-<NNN>
Change:  <STATE>-CHG-<YYYY>-<NNN>
```

Identifiers remain stable after closure. Closed records are retained.

## 6. Workbook usability

All workbooks should:

- have a distinct title row and header row;
- freeze the header area;
- enable filters;
- wrap long text;
- use readable widths with capped narrative columns;
- apply data validation to controlled fields;
- use restrained status/priority colours; and
- contain no hidden calculation needed to interpret a row.

