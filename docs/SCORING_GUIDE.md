# Scoring Guide

LiveHighlightEngine combines multiple normalized signals into one candidate score.

## Default formula

```text
score = audio * 0.25
      + danmaku * 0.35
      + ocr * 0.15
      + keyword * 0.25
```

All input signals are clamped to the range `0.0` to `1.0` before scoring.

## Signal interpretation

| Signal | Typical meaning | Common failure mode |
|---|---|---|
| `audio` | sudden loudness, laughter, shouting, impact | music and sound effects create false peaks |
| `danmaku` | audience reaction density | opening greetings or spam create false peaks |
| `ocr` | visible score, notification, result, or UI change | overlays and static text are repeatedly detected |
| `keyword` | transcript or OCR term match | isolated words lack context |

## Tuning procedure

1. Label at least 30 positive and 30 negative candidate intervals.
2. Normalize every signal using the same procedure used in production.
3. Start from the default weights.
4. Change one weight at a time.
5. Keep the weight sum equal to `1.0`.
6. Evaluate with ClipBench at multiple IoU thresholds.
7. Record precision, recall, F1, and boundary error.
8. Preserve the selected configuration with a project identifier and version.

## Threshold guidance

- Lower thresholds increase recall and review workload.
- Higher thresholds increase precision but may miss weaker narrative moments.
- Thresholds should be calibrated per content category rather than copied globally.

## Avoiding false peaks

- Ignore initial audience greetings when they are not content highlights.
- Normalize danmaku against a rolling baseline.
- Deduplicate repeated OCR text.
- Require agreement between at least two independent signals for high-confidence output.
- Apply minimum and maximum duration limits after interval expansion.

## Change control

Every production weight change should include the old configuration, new configuration, benchmark dataset version, metric comparison, and a short explanation of the trade-off.
