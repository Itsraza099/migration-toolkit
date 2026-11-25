# 0001. A config-driven, dry-run-first migration

- Status: Proposed
- Date: 2026-11-25

## Context
Migrations fail in predictable ways: unmapped fields, duplicates, silent row loss, and
no way back. The toolkit should make each of those visible before cutover.

## Decision
- Mappings live in **YAML specs** validated by Pydantic, not in Python code.
- Every run can be a **dry run** that maps and counts but writes nothing.
- Loads are **upserts keyed on the legacy id**, tagged with a `batch_id`, so a re-run
  updates rather than duplicates, and a batch can be rolled back.
- **Fuzzy matching** (rapidfuzz `token_sort_ratio`) puts each record in an auto / review /
  new band; only the review band needs a person.
- **Control totals** (row counts and sums) are taken on both sides and reconciled.
- Bank details are checked with [ukbankcheck](https://github.com/Itsraza099/ukbankcheck)
  once its modulus check is released.

## Alternatives considered
- One-off SQL scripts: fast to write, hard to review, impossible to re-run safely.
- An ETL tool (e.g. Talend): powerful, but hides the logic this project is meant to show.
- Exact-match dedupe only: misses "Acme Widgets Ltd" vs "Acme Widgets Limited".

## Consequences
Thresholds (92 / 75) are guesses until tested against labelled sample data.
