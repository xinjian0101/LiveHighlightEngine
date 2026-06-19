# Benchmark Integration

LiveHighlightEngine can export candidate intervals for evaluation with ClipBench.

## Recommended workflow

1. Produce candidate intervals from one recording.
2. Review and freeze the engine configuration.
3. Store predictions as a JSON array containing `start` and `end`.
4. Store manually reviewed ground truth in the same time base.
5. Evaluate at IoU thresholds such as `0.3`, `0.5`, and `0.7`.
6. Record configuration version, source identifier, and benchmark revision.

## Prediction conversion

LiveHighlightEngine output contains additional fields:

```json
{
  "start": 12.0,
  "end": 25.0,
  "score": 0.84,
  "reasons": ["danmaku", "keyword"],
  "text": "turning point continued reaction"
}
```

ClipBench only requires:

```json
{
  "start": 12.0,
  "end": 25.0
}
```

Do not discard the full engine output. Keep it as an audit artifact and derive the minimal benchmark file from it.

## Evaluation matrix

| Configuration | IoU threshold | Precision | Recall | F1 | Boundary error |
|---|---:|---:|---:|---:|---:|
| default-v1 | 0.30 | pending | pending | pending | pending |
| default-v1 | 0.50 | pending | pending | pending | pending |
| default-v1 | 0.70 | pending | pending | pending | pending |

## Regression policy

A scoring change should not be accepted only because one metric improves. Review:

- precision and recall trade-off;
- boundary error;
- duplicate candidate rate;
- average review time;
- performance on each content category;
- failures on long recordings.

## Reproducibility metadata

Store the engine commit SHA, configuration checksum, ClipBench commit SHA, annotation policy version, and input checksum with every published comparison.
