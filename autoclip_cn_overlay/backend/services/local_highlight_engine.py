from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from typing import Any, Iterable, Mapping

DEFAULT_WEIGHTS = {"audio": 0.25, "danmaku": 0.35, "ocr": 0.15, "keyword": 0.25}


@dataclass(frozen=True)
class SignalEvent:
    start: float
    end: float
    audio: float = 0.0
    danmaku: float = 0.0
    ocr: float = 0.0
    keyword: float = 0.0
    text: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class HighlightCandidate:
    start: float
    end: float
    score: float
    grade: str
    reasons: list[str]
    text: str


def normalize_weights(weights: Mapping[str, float] | None = None) -> dict[str, float]:
    source = dict(DEFAULT_WEIGHTS if weights is None else weights)
    if set(source) != set(DEFAULT_WEIGHTS):
        raise ValueError("权重必须同时包含 audio、danmaku、ocr、keyword")
    values = {key: float(value) for key, value in source.items()}
    if any(not math.isfinite(value) or value < 0 for value in values.values()):
        raise ValueError("权重必须是有限的非负数")
    total = sum(values.values())
    if total <= 0:
        raise ValueError("至少一个权重必须大于 0")
    return {key: value / total for key, value in values.items()}


def grade(score: float) -> str:
    if score >= 0.85:
        return "S"
    if score >= 0.70:
        return "A"
    if score >= 0.55:
        return "B"
    return "C"


def score_event(event: SignalEvent, weights: Mapping[str, float] | None = None, reason_threshold: float = 0.70) -> HighlightCandidate:
    if event.start < 0 or event.end <= event.start:
        raise ValueError("事件时间区间无效")
    normalized = normalize_weights(weights)
    values = {key: min(1.0, max(0.0, float(getattr(event, key)))) for key in DEFAULT_WEIGHTS}
    score = round(sum(values[key] * normalized[key] for key in normalized), 4)
    reasons = [key for key, value in values.items() if value >= reason_threshold]
    return HighlightCandidate(event.start, event.end, score, grade(score), reasons, event.text)


def merge_candidates(items: list[HighlightCandidate], gap_seconds: float) -> list[HighlightCandidate]:
    if gap_seconds < 0:
        raise ValueError("合并间隔不能小于 0")
    merged: list[HighlightCandidate] = []
    for item in sorted(items, key=lambda value: (value.start, value.end)):
        if not merged or item.start - merged[-1].end > gap_seconds:
            merged.append(item)
            continue
        previous = merged[-1]
        best_score = max(previous.score, item.score)
        merged[-1] = HighlightCandidate(
            previous.start,
            max(previous.end, item.end),
            best_score,
            grade(best_score),
            sorted(set(previous.reasons + item.reasons)),
            " ".join(part for part in (previous.text, item.text) if part),
        )
    return merged


def select_highlights(events: Iterable[SignalEvent], *, threshold: float = 0.45, gap_seconds: float = 5.0, max_results: int = 10, weights: Mapping[str, float] | None = None, reason_threshold: float = 0.70) -> list[dict[str, Any]]:
    if not 0 <= threshold <= 1:
        raise ValueError("阈值必须在 0 到 1 之间")
    if max_results not in (5, 10, 15, 20, 25, 30):
        raise ValueError("切片数量只能是 5、10、15、20、25、30")
    scored = [score_event(event, weights, reason_threshold) for event in events]
    merged = merge_candidates([item for item in scored if item.score >= threshold], gap_seconds)
    ranked = sorted(merged, key=lambda item: (-item.score, item.start))[:max_results]
    return [asdict(item) for item in ranked]
