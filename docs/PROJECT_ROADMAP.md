# Project Roadmap

This roadmap distinguishes current behavior from planned work. Items below are proposals until code, tests, and release notes are committed.

## Current baseline

- JSONL event input
- Rule-based multi-signal scoring
- Threshold filtering
- Adjacent interval merging
- Ranked JSON output
- Local execution without a paid API

## Phase 1: input reliability

### Planned work

- Reject non-finite scores and invalid time ranges.
- Add configurable clamping for signals outside 0—1.
- Report malformed-line counts instead of silently losing records.
- Add deterministic fixture generation for regression tests.

### Acceptance criteria

- Invalid `start >= end` records fail with a precise line number.
- Duplicate input lines are handled consistently.
- The same input and configuration produce byte-stable output.

## Phase 2: scoring calibration

### Planned work

- Move weights into a versioned configuration file.
- Add per-content presets without changing the default behavior.
- Record score contributions for every signal.
- Add threshold sweep reports.

### Acceptance criteria

- Every result exposes a reproducible contribution breakdown.
- Presets are versioned and covered by tests.
- Calibration reports include Precision, Recall, F1, and duplicate rate.

## Phase 3: interval quality

### Planned work

- Add configurable pre-roll and post-roll.
- Improve overlap and near-duplicate suppression.
- Preserve context when a peak occurs near a segment boundary.
- Add maximum and minimum candidate duration policies.

### Acceptance criteria

- Boundary changes are measured through ClipBench.
- Merging never creates a negative or zero-length interval.
- Regression fixtures cover adjacent, nested, and overlapping windows.

## Phase 4: long-recording performance

### Planned work

- Stream JSONL instead of loading all events when possible.
- Add chunked processing with deterministic cross-chunk merging.
- Record processing time and peak memory on reproducible fixtures.

### Acceptance criteria

- A multi-hour fixture can be processed without unbounded memory growth.
- Chunked and non-chunked output remain equivalent within documented rules.

## Phase 5: integration

### Planned work

- Provide a stable export adapter for ClipBench.
- Provide a reviewed-interval handoff format for FlowFFmpeg.
- Add a machine-readable configuration manifest.

### Acceptance criteria

- Integration examples run from a clean checkout.
- Every exported artifact includes source, configuration, and version metadata.

## Non-goals

- Automatically publishing clips
- Replacing human editorial review
- Performing copyright or legal clearance
- Claiming universal highlight quality across all content types
