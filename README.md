<div align="center">

# LiveHighlightEngine

**Explainable, local-first highlight candidate ranking for long recordings.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-2ea44f)](LICENSE)
[![Processing](https://img.shields.io/badge/Processing-Local--first-6f42c1)](ABOUT.md)
[![Status](https://img.shields.io/badge/Status-Active%20MVP-f59e0b)](MAINTENANCE_TRACE.md)

[Quick start](#quick-start) · [Capabilities](#capability-matrix) · [Examples](examples/events.jsonl) · [Architecture](docs/ARCHITECTURE.md) · [About](ABOUT.md) · [Contributing](CONTRIBUTING.md)

</div>

---

LiveHighlightEngine turns prepared audio, audience-message, OCR, and keyword signals into ranked, reviewable time intervals. It is designed for editors and developers who need deterministic candidate selection without uploading source media or calling paid APIs.

> [!IMPORTANT]
> The output is a review queue, not a finished edit. Human approval remains required for context, rights, privacy, continuity, and publication decisions.

## At a glance

| Area | Current support |
|---|---|
| Input | JSONL event windows |
| Signals | Audio, audience messages, OCR, keywords |
| Ranking | Configurable weighted scoring |
| Selection | Threshold, merge gap, result limit |
| Exports | JSON, CSV, Markdown |
| Evaluation | ClipBench integration |
| Runtime | Python standard library, local execution |

## Quick start

```bash
python main.py examples/events.jsonl \
  --config configs/default.json \
  --threshold 0.45 \
  --top 10 \
  --format markdown \
  -o highlights.md
```

Run the test suite:

```bash
python -m unittest -v
```

## Capability matrix

| Capability | Status | Notes |
|---|---:|---|
| Weighted multi-signal scoring | ✅ | Profiles are loaded from JSON |
| Event validation | ✅ | Rejects invalid and non-finite timestamps |
| Adjacent interval merging | ✅ | Configurable merge gap |
| Explainable trigger reasons | ✅ | Retained in every result |
| Multi-format reports | ✅ | JSON, CSV, and Markdown |
| Raw video decoding | ⏳ | Planned adapter layer |
| Automatic publishing | ❌ | Intentionally outside scope |

## Input contract

Each JSONL line represents one candidate window:

```json
{
  "start": 12.0,
  "end": 25.0,
  "audio": 0.62,
  "danmaku": 0.91,
  "ocr": 0.35,
  "keyword": 0.80,
  "text": "Audience reaction after a key turning point",
  "source_id": "recording-001",
  "metadata": {"category": "gaming"}
}
```

| Field | Type | Required | Description |
|---|---|---:|---|
| `start` | number | yes | Start time in seconds |
| `end` | number | yes | End time in seconds |
| `audio` | number | no | Normalized audio signal |
| `danmaku` | number | no | Normalized audience-message signal |
| `ocr` | number | no | Normalized OCR signal |
| `keyword` | number | no | Normalized keyword signal |
| `text` | string | no | Human-review context |
| `source_id` | string | no | Source recording identifier |
| `metadata` | object | no | Adapter-specific review metadata |

## Output formats

```bash
python main.py examples/events.jsonl --format json -o report.json
python main.py examples/events.jsonl --format csv -o report.csv
python main.py examples/events.jsonl --format markdown -o report.md
```

Reports include candidate count, total selected duration, average score, reason counts, timing, score, reasons, and review context.

## Recommended workflow

```text
signal adapters
      ↓
validated JSONL events
      ↓
versioned scoring profile
      ↓
threshold + merge + ranking
      ↓
human review
      ↓
ClipBench evaluation / FlowFFmpeg export
```

## Repository map

| Path | Purpose |
|---|---|
| `main.py` | CLI, scoring, merging, and exports |
| `configs/` | Versioned scoring profiles |
| `schema/` | Event contract |
| `examples/` | Synthetic input fixtures |
| `docs/` | Architecture, scoring, and integration guides |
| `test_*.py` | Functional and export regression tests |
| `ABOUT.md` | Mission, maturity, boundaries, and governance |

## Project boundaries

- No source-video upload
- No hidden network request
- No automatic FFmpeg execution
- No rights or policy determination
- No claim that rule-based scoring is universally optimal

## Project documentation

- [About the project](ABOUT.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Scoring guide](docs/SCORING_GUIDE.md)
- [ClipBench integration](docs/BENCHMARK_INTEGRATION.md)
- [Error handling](docs/ERROR_HANDLING.md)
- [Maintenance trace](MAINTENANCE_TRACE.md)
- [Changelog](CHANGELOG.md)

## License

MIT
