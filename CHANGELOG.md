# Changelog

All notable changes to this project are documented here.

## Unreleased

### Added

- Versioned scoring-profile loading through `--config`.
- Configurable weights, selection threshold, merge gap, result limit, and reason threshold.
- Formal event validation for timestamps and signal values.
- Compatibility fields for `source_id` and structured `metadata`.
- Tests for profile normalization, invalid events, metadata loading, and custom scoring.
- Architecture documentation covering ingestion, normalization, scoring, merging, ranking, and export.
- Versioned default and review-oriented scoring configurations.
- Formal event record schema.
- ClipBench regression-integration guidance.
- Input validation and error-handling contract.

### Changed

- Weight profiles are normalized before scoring, allowing any positive proportional values.
- CLI arguments now override configuration-file selection values.
- Malformed event records include their JSONL line number in the raised error.
- The primary README and examples are maintained in English.

### Known limitations

- The CLI still consumes prepared event signals rather than raw media.
- Configuration files are loaded directly but are not yet validated against JSON Schema at runtime.
- Candidate merging retains the strongest score rather than recalculating a duration-weighted score.
- Rights, privacy, factual accuracy, and delivery policy remain outside the scoring engine.

## 0.1.0 — 2026-06-19

Initial executable MVP with multi-signal scoring, thresholding, interval merging, ranking, and JSON export.

## Maintenance policy

- Every behavior change must include tests.
- New adapters require non-sensitive fixtures.
- Scoring changes require benchmark comparison through ClipBench.
- Backward-incompatible event fields require a schema-version increment.
- User-facing repository content is maintained in English.
