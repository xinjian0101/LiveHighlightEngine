# Changelog

All notable changes to this project are documented here.

## Unreleased

### Added

- Architecture documentation covering ingestion, normalization, scoring, merging, ranking, and export.
- Versioned default and review-oriented scoring configurations.
- Formal event record schema.
- Scoring calibration guidance.
- ClipBench integration guidance.
- Input validation and error-handling contract.
- English-only repository entry point and examples.
- Runnable JSONL event fixture.
- Unit smoke test and GitHub Actions validation workflow.
- Public roadmap issue for real media signal adapters.

### Changed

- The primary README is now fully English.
- The MVP documentation now describes deterministic processing boundaries, review requirements, downstream integration, and configuration traceability.

### Known limitations

- The current CLI consumes precomputed event signals rather than raw media.
- Configuration files are documented but not yet loaded directly by the CLI.
- Candidate merging retains the strongest score rather than recalculating a duration-weighted score.
- Rights, privacy, factual accuracy, and delivery policy remain outside the scoring engine.

## 0.1.0 — 2026-06-19

Initial executable MVP with multi-signal scoring, thresholding, interval merging, ranking, and JSON export.

## Maintenance policy

- Every user-visible change must update this changelog.
- New adapters require non-sensitive fixtures.
- Scoring changes require benchmark comparison through ClipBench.
- Backward-incompatible event fields require a schema-version increment.
- User-facing repository content is maintained in English.
