# LiveHighlightEngine

A local-first highlight candidate engine for long live-stream recordings. The project combines normalized audio, audience-reaction, OCR, and keyword signals into reviewable time intervals that can be ranked, inspected, and passed to downstream editing tools.

> Status: lightweight MVP and algorithm prototype. It does not call paid APIs, upload source video, or execute media editing commands.

## Use cases

- Initial highlight screening for multi-hour live-stream recordings
- Candidate extraction from gaming, commerce, interviews, sports, and talk content
- Experiments that combine audience-reaction peaks, keyword hits, OCR changes, and audio intensity
- Structured candidate delivery to a human editing workstation
- Regression evaluation with ClipBench

## Current capabilities

- Weighted scoring across `audio`, `danmaku`, `ocr`, and `keyword` signals
- Optional `text` context for human review
- Merging of adjacent or overlapping candidate intervals
- Threshold-based filtering
- Score-based ranking with a configurable result limit
- JSON output containing timing, score, trigger reasons, and context
- Fully local execution with no mandatory third-party dependency

## Quick start

### Requirements

- Python 3.10 or newer
- No mandatory third-party package

### Run

```bash
python main.py examples/events.jsonl --threshold 0.45 --top 10 -o highlights.json
```

### Test

```bash
python -m unittest -v
```

## Input format

The input is JSONL: one event or candidate window per line.

| Field | Type | Required | Description |
|---|---|---:|---|
| `start` | number | yes | interval start in seconds |
| `end` | number | yes | interval end in seconds |
| `audio` | number | no | normalized audio intensity or reaction signal |
| `danmaku` | number | no | normalized audience-message density signal |
| `ocr` | number | no | normalized OCR event signal |
| `keyword` | number | no | normalized keyword-match signal |
| `text` | string | no | short context used during human review |

Example:

```json
{"start":12.0,"end":25.0,"audio":0.62,"danmaku":0.91,"ocr":0.35,"keyword":0.80,"text":"Audience reaction after a key turning point"}
```

## Output example

```json
[
  {
    "start": 12.0,
    "end": 25.0,
    "score": 0.84,
    "reasons": ["danmaku", "keyword"],
    "text": "Audience reaction after a key turning point"
  }
]
```

The output is a candidate list, not a finished edit. Review context, rights, privacy, continuity, and platform requirements before publishing.

## Recommended workflow

1. Generate time-window events from media, chat, transcript, or OCR modules.
2. Normalize signals to a consistent range.
3. Run scoring with a versioned configuration.
4. Review duplicates, incomplete context, and false peaks.
5. Pass approved intervals to an editor or a FlowFFmpeg workflow.
6. Evaluate predictions against reviewed ground truth with ClipBench.

## Design principles

- **Local first**: source media does not need to leave the machine.
- **Explainable**: results retain trigger signals and review context.
- **Reproducible**: fixed input and configuration should produce stable output.
- **Composable**: candidate selection is separate from playback and editing.
- **Human controlled**: the engine narrows the search space; people make publication decisions.

## Known limitations

- The scoring model is rule-based rather than a generally trained model.
- Poor input signals can create false peaks.
- The tool does not assess copyright, privacy, factual accuracy, or platform policy.
- It does not read raw video or execute FFmpeg.
- Very large recordings should use segmented preprocessing.

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Scoring Guide](docs/SCORING_GUIDE.md)
- [Benchmark Integration](docs/BENCHMARK_INTEGRATION.md)
- [Error Handling](docs/ERROR_HANDLING.md)
- [Contribution Guide](CONTRIBUTING.md)
- [Maintenance Trace](MAINTENANCE_TRACE.md)

## Related projects

- **ClipBench** evaluates temporal predictions with precision, recall, F1, IoU, and boundary error.
- **FlowFFmpeg** compiles approved media workflows into inspectable FFmpeg commands.

## License

MIT
