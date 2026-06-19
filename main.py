from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Mapping


@dataclass(frozen=True)
class Event:
    start: float
    end: float
    audio: float = 0.0
    danmaku: float = 0.0
    ocr: float = 0.0
    keyword: float = 0.0
    text: str = ""
    source_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Highlight:
    start: float
    end: float
    score: float
    reasons: list[str]
    text: str


DEFAULT_WEIGHTS = {"audio": 0.25, "danmaku": 0.35, "ocr": 0.15, "keyword": 0.25}


def validate_weights(weights: Mapping[str, float]) -> dict[str, float]:
    missing = set(DEFAULT_WEIGHTS) - set(weights)
    unknown = set(weights) - set(DEFAULT_WEIGHTS)
    if missing:
        raise ValueError(f"Missing weight keys: {', '.join(sorted(missing))}")
    if unknown:
        raise ValueError(f"Unknown weight keys: {', '.join(sorted(unknown))}")
    normalized = {name: float(weights[name]) for name in DEFAULT_WEIGHTS}
    if any(not math.isfinite(value) or value < 0 for value in normalized.values()):
        raise ValueError("Weights must be finite non-negative numbers")
    total = sum(normalized.values())
    if total <= 0:
        raise ValueError("At least one weight must be positive")
    return {name: value / total for name, value in normalized.items()}


def validate_event(event: Event) -> None:
    if not math.isfinite(event.start) or not math.isfinite(event.end):
        raise ValueError("Event timestamps must be finite")
    if event.start < 0:
        raise ValueError("Event start must be non-negative")
    if event.end <= event.start:
        raise ValueError("Event end must be greater than start")
    for name in DEFAULT_WEIGHTS:
        value = getattr(event, name)
        if not math.isfinite(value):
            raise ValueError(f"Event signal {name} must be finite")


def load_config(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Configuration must be a JSON object")
    return value


def score_event(
    event: Event,
    weights: Mapping[str, float] | None = None,
    reason_threshold: float = 0.7,
) -> Highlight:
    validate_event(event)
    effective_weights = validate_weights(weights or DEFAULT_WEIGHTS)
    values = {
        "audio": min(1.0, max(0.0, event.audio)),
        "danmaku": min(1.0, max(0.0, event.danmaku)),
        "ocr": min(1.0, max(0.0, event.ocr)),
        "keyword": min(1.0, max(0.0, event.keyword)),
    }
    score = sum(values[name] * effective_weights[name] for name in effective_weights)
    reasons = [name for name, value in values.items() if value >= reason_threshold]
    return Highlight(event.start, event.end, round(score, 4), reasons, event.text)


def merge_highlights(items: list[Highlight], gap: float) -> list[Highlight]:
    if gap < 0:
        raise ValueError("Merge gap must be non-negative")
    merged: list[Highlight] = []
    for item in sorted(items, key=lambda value: (value.start, value.end)):
        if not merged or item.start - merged[-1].end > gap:
            merged.append(item)
            continue
        previous = merged[-1]
        merged[-1] = Highlight(
            previous.start,
            max(previous.end, item.end),
            round(max(previous.score, item.score), 4),
            sorted(set(previous.reasons + item.reasons)),
            " ".join(part for part in (previous.text, item.text) if part),
        )
    return merged


def select(
    events: list[Event],
    threshold: float = 0.45,
    gap: float = 5.0,
    top: int = 10,
    weights: Mapping[str, float] | None = None,
    reason_threshold: float = 0.7,
) -> list[dict]:
    if not 0 <= threshold <= 1:
        raise ValueError("Threshold must be between 0 and 1")
    if top < 0:
        raise ValueError("Top must be non-negative")
    candidates = [score_event(event, weights, reason_threshold) for event in events]
    merged = merge_highlights([item for item in candidates if item.score >= threshold], gap)
    return [asdict(item) for item in sorted(merged, key=lambda item: (-item.score, item.start))[:top]]


def load_events(path: str) -> list[Event]:
    events: list[Event] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                raw = json.loads(line)
                if not isinstance(raw, dict):
                    raise TypeError("event must be a JSON object")
                event = Event(**raw)
                validate_event(event)
                events.append(event)
            except (TypeError, ValueError, json.JSONDecodeError) as exc:
                raise ValueError(f"Invalid JSONL event at line {line_number}: {exc}") from exc
    return events


def main() -> None:
    parser = argparse.ArgumentParser(description="Score live-stream highlight intervals.")
    parser.add_argument("events")
    parser.add_argument("-o", "--output", default="highlights.json")
    parser.add_argument("--config")
    parser.add_argument("--threshold", type=float)
    parser.add_argument("--gap", type=float)
    parser.add_argument("--top", type=int)
    args = parser.parse_args()

    config = load_config(args.config)
    selection = config.get("selection", {}) if isinstance(config.get("selection", {}), dict) else {}
    weights = config.get("weights", DEFAULT_WEIGHTS)
    threshold = args.threshold if args.threshold is not None else float(selection.get("threshold", 0.45))
    gap = args.gap if args.gap is not None else float(selection.get("merge_gap_seconds", 5.0))
    top = args.top if args.top is not None else int(selection.get("max_results", 10))
    reason_threshold = float(config.get("reason_threshold", 0.7))

    result = select(load_events(args.events), threshold, gap, top, weights, reason_threshold)
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(result)} highlights to {args.output}")


if __name__ == "__main__":
    main()
