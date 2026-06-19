# Architecture

LiveHighlightEngine separates signal ingestion, normalization, scoring, interval merging, ranking, and export.

## Processing stages

1. **Input adapters** convert external metadata into a common event record.
2. **Normalization** clamps each signal to the range `0.0` to `1.0`.
3. **Weighted scoring** combines audio, danmaku, OCR, and keyword signals.
4. **Thresholding** removes weak candidates before interval operations.
5. **Merging** joins nearby candidates while preserving the strongest score.
6. **Ranking** sorts merged intervals by score and start time.
7. **Export** writes deterministic JSON for downstream clipping tools.

## Event contract

```json
{
  "start": 12.0,
  "end": 18.0,
  "audio": 0.82,
  "danmaku": 0.91,
  "ocr": 0.20,
  "keyword": 0.80,
  "text": "turning point"
}
```

`start` and `end` are seconds. Optional signal values outside the valid range are clamped.

## Design principles

- Local-first execution.
- No hidden network calls.
- Deterministic output for the same input and configuration.
- Small standard-library core.
- Adapters remain separate from scoring logic.
- User-provided metadata is treated as untrusted input.

## Planned extension points

- XML and JSON danmaku adapters.
- FFprobe metadata adapter.
- Per-channel weight profiles.
- Duplicate-candidate suppression.
- CSV and EDL export.
- Batch evaluation through ClipBench.
