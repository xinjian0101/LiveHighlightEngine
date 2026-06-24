from __future__ import annotations

import csv
import json
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

DEFAULT_KEYWORDS = {
    "reaction": ["卧槽", "牛", "厉害", "666", "逆天", "离谱", "笑死", "高能", "名场面"],
    "turning_point": ["反转", "翻盘", "赢了", "输了", "结束", "关键", "绝杀", "爆了"],
    "emotion": ["哈哈", "呜呜", "哭了", "生气", "激动", "震惊", "害怕"],
}


def _keyword_score(texts: Iterable[str]) -> float:
    joined = "\n".join(texts).lower()
    hits = sum(joined.count(word.lower()) for words in DEFAULT_KEYWORDS.values() for word in words)
    return min(1.0, hits / 8.0)


def _normalize_counts(counts: dict[int, int]) -> dict[int, float]:
    if not counts:
        return {}
    ordered = sorted(counts.values())
    p95 = ordered[max(0, int(len(ordered) * 0.95) - 1)] or 1
    return {bucket: min(1.0, count / p95) for bucket, count in counts.items()}


def parse_bilibili_xml(path: str | Path, *, bucket_seconds: int = 10, danmaku_delay_seconds: float = 10.0, window_seconds: float = 45.0) -> list[dict[str, Any]]:
    root = ET.parse(Path(path)).getroot()
    messages: dict[int, list[str]] = defaultdict(list)
    for node in root.findall(".//d"):
        raw = node.attrib.get("p", "").split(",")
        if not raw:
            continue
        try:
            timestamp = max(0.0, float(raw[0]) - danmaku_delay_seconds)
        except ValueError:
            continue
        bucket = int(timestamp // bucket_seconds) * bucket_seconds
        text = "".join(node.itertext()).strip()
        if text:
            messages[bucket].append(text)
    normalized = _normalize_counts({bucket: len(items) for bucket, items in messages.items()})
    return [
        {
            "start": float(bucket),
            "end": float(bucket + window_seconds),
            "audio": 0.0,
            "danmaku": normalized.get(bucket, 0.0),
            "ocr": 0.0,
            "keyword": _keyword_score(texts),
            "text": " / ".join(texts[:8]),
            "metadata": {"source": "bilibili_xml", "message_count": len(texts)},
        }
        for bucket, texts in sorted(messages.items())
    ]


def parse_generic_danmaku(path: str | Path, *, bucket_seconds: int = 10) -> list[dict[str, Any]]:
    source = Path(path)
    rows: list[tuple[float, str]] = []
    if source.suffix.lower() in {".json", ".jsonl"}:
        text = source.read_text(encoding="utf-8")
        values = json.loads(text) if source.suffix.lower() == ".json" else [json.loads(line) for line in text.splitlines() if line.strip()]
        if isinstance(values, dict):
            values = values.get("messages", [])
        for item in values:
            rows.append((float(item.get("time", item.get("timestamp", 0))), str(item.get("text", item.get("content", "")))))
    elif source.suffix.lower() == ".csv":
        with source.open("r", encoding="utf-8-sig", newline="") as handle:
            for item in csv.DictReader(handle):
                rows.append((float(item.get("time", item.get("timestamp", 0)) or 0), str(item.get("text", item.get("content", "")))))
    else:
        raise ValueError("弹幕文件仅支持 XML、JSON、JSONL、CSV")
    grouped: dict[int, list[str]] = defaultdict(list)
    for timestamp, text in rows:
        grouped[int(max(0.0, timestamp) // bucket_seconds) * bucket_seconds].append(text)
    normalized = _normalize_counts({bucket: len(items) for bucket, items in grouped.items()})
    return [
        {
            "start": float(bucket),
            "end": float(bucket + 45),
            "audio": 0.0,
            "danmaku": normalized.get(bucket, 0.0),
            "ocr": 0.0,
            "keyword": _keyword_score(texts),
            "text": " / ".join(texts[:8]),
            "metadata": {"source": "danmaku_file", "message_count": len(texts)},
        }
        for bucket, texts in sorted(grouped.items())
    ]


def load_danmaku_events(path: str | Path, **kwargs: Any) -> list[dict[str, Any]]:
    source = Path(path)
    if source.suffix.lower() == ".xml":
        return parse_bilibili_xml(source, **kwargs)
    return parse_generic_danmaku(source, bucket_seconds=int(kwargs.get("bucket_seconds", 10)))
