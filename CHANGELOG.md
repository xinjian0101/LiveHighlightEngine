# Changelog

All notable changes to this project are documented here.

## Unreleased

### Added

- Architecture documentation covering ingestion, normalization, scoring, merging, ranking, and export.
- Versioned default scoring configuration under `configs/default.json`.
- Runnable JSONL event example.
- Unit smoke test for highlight selection.
- GitHub Actions validation workflow.
- Public roadmap issue for real media signal adapters.

### Changed

- The MVP now documents deterministic processing boundaries and downstream integration points.

### Known limitations

- The current CLI consumes precomputed event signals rather than raw media.
- Weight profiles are defined in code; configuration loading is planned.
- Candidate merging retains the strongest score rather than recalculating a duration-weighted score.

## 0.1.0 — 2026-06-19

Initial executable MVP with multi-signal scoring, thresholding, interval merging, ranking, and JSON export.

## Maintenance policy

- Every user-visible change must update this changelog.
- New adapters require fixtures that do not contain private user data.
- Scoring changes require benchmark comparison through ClipBench.
- Backward-incompatible event fields require a schema-version increment.
