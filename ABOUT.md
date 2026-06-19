# About LiveHighlightEngine

## Mission

LiveHighlightEngine reduces the review cost of long recordings by turning prepared event signals into explainable highlight candidates.

## Intended users

- Video editors screening multi-hour recordings
- Developers building local media-analysis tools
- Researchers evaluating temporal highlight selection
- Teams that need deterministic, reviewable candidate intervals

## What it does

The engine scores normalized audio, audience-message, OCR, and keyword signals, merges nearby intervals, ranks the results, and exports structured candidates for human review or downstream editing.

## What it does not do

- Decode source video
- Run speech recognition
- Execute FFmpeg
- Make publication decisions
- Determine copyright, privacy, or platform compliance

## Architecture

```text
Adapters -> normalized events -> validation -> weighted scoring
         -> thresholding -> interval merge -> ranking -> export
```

## Design priorities

1. Local-first processing
2. Deterministic results
3. Explainable scoring
4. Stable event contracts
5. Human approval before export
6. Reproducible benchmark comparison

## Maturity

The project is an executable MVP with configurable scoring, event validation, JSONL ingestion, tests, schemas, and ClipBench integration guidance. Raw-media adapters and larger public benchmarks remain future work.

## Compatibility

Stable event fields include `start`, `end`, `audio`, `danmaku`, `ocr`, `keyword`, `text`, `source_id`, and `metadata`.

## Related repositories

- `ClipBench` for temporal evaluation
- `FlowFFmpeg` for inspected media-command generation

## Governance

Behavior changes require tests. Scoring changes require a documented configuration and benchmark comparison. Public documentation and examples are maintained in English.
