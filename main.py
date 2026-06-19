from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Event:
    start: float
    end: float
    audio: float = 0.0
    danmaku: float = 0.0
    ocr: float = 0.0
    keyword: float = 0.0
    text: str = ""


@dataclass(frozen=True)
class Highlight:
    start: float
    end: float
    score: float
    reasons: list[str]
    text: str


WEIGHTS = {"audio": 0.25, "danmaku": 0.35, "ocr": 0.15, "keyword": 0.25}


def score_event(event: Event) -> Highlight:
    values = {
        "audio": min(1.0, max(0.0, event.audio)),
        "danmaku": min(1.0, max(0.0, event.danmaku)),
        "ocr": min(1.0, max(0.0, event.ocr)),
        "keyword": min(1.0, max(0.0, event.keyword)),
    }
    score = sum(values[name] * WEIGHTS[name] for name in WEIGHTS)
    reasons = [name for name, value in values.items() if value >= 0.7]
    return Highlight(event.start, event.end, round(score, 4), reasons, event.text)


def merge_highlights(items: list[Highlight], gap: float) -> list[Highlight]:
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


def select(events: list[Event], threshold: float = 0.45, gap: float = 5.0, top: int = 10) -> list[dict]:
    candidates = [score_event(event) for event in events]
    merged = merge_highlights([item for item in candidates if item.score >= threshold], gap)
    return [asdict(item) for item in sorted(merged, key=lambda item: (-item.score, item.start))[:top]]


def load_events(path: str) -> list[Event]:
    events: list[Event] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                events.append(Event(**json.loads(line)))
            except (TypeError, json.JSONDecodeError) as exc:
                raise ValueError(f"Invalid JSONL event at line {line_number}: {exc}") from exc
    return events


def main() -> None:
    parser = argparse.ArgumentParser(description="Score live-stream highlight intervals.")
    parser.add_argument("events")
    parser.add_argument("-o", "--output", default="highlights.json")
    parser.add_argument("--threshold", type=float, default=0.45)
    parser.add_argument("--gap", type=float, default=5.0)
    parser.add_argument("--top", type=int, default=10)
    args = parser.parse_args()
    result = select(load_events(args.events), args.threshold, args.gap, args.top)
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(result)} highlights to {args.output}")


if __name__ == "__main__":
    main()
