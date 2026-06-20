from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Mapping

from clip_export import PLATFORM_PRESETS, ClipExportError, export_highlights


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
REASON_NAMES_CN = {
    "audio": "音频峰值",
    "danmaku": "弹幕热度",
    "ocr": "画面文字",
    "keyword": "关键词",
}


def validate_weights(weights: Mapping[str, float]) -> dict[str, float]:
    missing = set(DEFAULT_WEIGHTS) - set(weights)
    unknown = set(weights) - set(DEFAULT_WEIGHTS)
    if missing:
        raise ValueError(f"缺少权重字段：{', '.join(sorted(missing))}")
    if unknown:
        raise ValueError(f"未知权重字段：{', '.join(sorted(unknown))}")
    normalized = {name: float(weights[name]) for name in DEFAULT_WEIGHTS}
    if any(not math.isfinite(value) or value < 0 for value in normalized.values()):
        raise ValueError("权重必须是有限的非负数")
    total = sum(normalized.values())
    if total <= 0:
        raise ValueError("至少一个权重必须大于 0")
    return {name: value / total for name, value in normalized.items()}


def validate_event(event: Event) -> None:
    if not math.isfinite(event.start) or not math.isfinite(event.end):
        raise ValueError("事件时间必须是有限数值")
    if event.start < 0:
        raise ValueError("事件开始时间不能小于 0")
    if event.end <= event.start:
        raise ValueError("事件结束时间必须大于开始时间")
    for name in DEFAULT_WEIGHTS:
        value = getattr(event, name)
        if not math.isfinite(value):
            raise ValueError(f"事件信号 {name} 必须是有限数值")


def load_config(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("配置文件必须是 JSON 对象")
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
        raise ValueError("合并间隔不能小于 0")
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
        raise ValueError("阈值必须在 0 到 1 之间")
    if top < 0:
        raise ValueError("输出数量不能小于 0")
    candidates = [score_event(event, weights, reason_threshold) for event in events]
    merged = merge_highlights([item for item in candidates if item.score >= threshold], gap)
    return [asdict(item) for item in sorted(merged, key=lambda item: (-item.score, item.start))[:top]]


def summarize_results(items: list[dict]) -> dict[str, Any]:
    reason_counts = Counter(reason for item in items for reason in item.get("reasons", []))
    total_duration = sum(max(0.0, float(item["end"]) - float(item["start"])) for item in items)
    average_score = sum(float(item["score"]) for item in items) / len(items) if items else 0.0
    return {
        "count": len(items),
        "total_duration_seconds": round(total_duration, 4),
        "average_score": round(average_score, 4),
        "reason_counts": dict(sorted(reason_counts.items())),
    }


def infer_output_format(path: str, requested: str | None = None) -> str:
    if requested:
        return requested
    suffix = Path(path).suffix.lower()
    return {".csv": "csv", ".md": "markdown", ".markdown": "markdown"}.get(suffix, "json")


def write_results(items: list[dict], path: str, output_format: str | None = None) -> None:
    output_format = infer_output_format(path, output_format)
    target = Path(path)
    if output_format == "json":
        target.write_text(
            json.dumps({"summary": summarize_results(items), "highlights": items}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return
    if output_format == "csv":
        with target.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=("start", "end", "duration", "score", "reasons", "text"))
            writer.writeheader()
            for item in items:
                writer.writerow({
                    "start": item["start"],
                    "end": item["end"],
                    "duration": round(float(item["end"]) - float(item["start"]), 4),
                    "score": item["score"],
                    "reasons": ";".join(REASON_NAMES_CN.get(name, name) for name in item.get("reasons", [])),
                    "text": item.get("text", ""),
                })
        return
    if output_format == "markdown":
        summary = summarize_results(items)
        lines = [
            "# 高光候选报告",
            "",
            f"- 候选数量：{summary['count']}",
            f"- 总时长：{summary['total_duration_seconds']} 秒",
            f"- 平均分：{summary['average_score']}",
            "",
            "| 开始 | 结束 | 时长 | 分数 | 触发原因 | 内容摘要 |",
            "|---:|---:|---:|---:|---|---|",
        ]
        for item in items:
            text = str(item.get("text", "")).replace("|", "\\|").replace("\n", " ")
            reasons = "、".join(REASON_NAMES_CN.get(name, name) for name in item.get("reasons", []))
            duration = round(float(item["end"]) - float(item["start"]), 4)
            lines.append(f"| {item['start']} | {item['end']} | {duration} | {item['score']} | {reasons} | {text} |")
        target.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return
    raise ValueError(f"不支持的输出格式：{output_format}")


def load_events(path: str) -> list[Event]:
    events: list[Event] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                raw = json.loads(line)
                if not isinstance(raw, dict):
                    raise TypeError("事件必须是 JSON 对象")
                event = Event(**raw)
                validate_event(event)
                events.append(event)
            except (TypeError, ValueError, json.JSONDecodeError) as exc:
                raise ValueError(f"第 {line_number} 行 JSONL 事件无效：{exc}") from exc
    return events


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="直播/长视频高光识别与多平台自动切片工具")
    parser.add_argument("events", help="高光信号 JSONL 文件")
    parser.add_argument("-o", "--output", default="highlights.json", help="高光结果文件")
    parser.add_argument("--format", choices=("json", "csv", "markdown"), help="结果格式")
    parser.add_argument("--config", help="评分配置 JSON 文件")
    parser.add_argument("--threshold", type=float, help="高光最低分，0-1")
    parser.add_argument("--gap", type=float, help="相邻片段合并间隔（秒）")
    parser.add_argument("--top", type=int, help="最多输出多少条高光")
    parser.add_argument("--video", help="源视频路径；填写后生成平台切片任务")
    parser.add_argument(
        "--platform",
        choices=tuple(PLATFORM_PRESETS),
        default="douyin",
        help="导出平台：bilibili、douyin、tiktok",
    )
    parser.add_argument("--export-dir", default="exports", help="切片输出目录")
    parser.add_argument("--layout", choices=("center", "fit"), default="center", help="画面布局：居中裁切或完整适配")
    parser.add_argument("--ffmpeg", default="ffmpeg", help="FFmpeg 可执行文件路径")
    parser.add_argument("--crf", type=int, default=20, help="H.264 画质参数，越小画质越高")
    parser.add_argument("--execute", action="store_true", help="实际执行 FFmpeg；不填写则只生成命令清单")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        config = load_config(args.config)
        selection = config.get("selection", {}) if isinstance(config.get("selection", {}), dict) else {}
        weights = config.get("weights", DEFAULT_WEIGHTS)
        threshold = args.threshold if args.threshold is not None else float(selection.get("threshold", 0.45))
        gap = args.gap if args.gap is not None else float(selection.get("merge_gap_seconds", 5.0))
        top = args.top if args.top is not None else int(selection.get("max_results", 10))
        reason_threshold = float(config.get("reason_threshold", 0.7))

        result = select(load_events(args.events), threshold, gap, top, weights, reason_threshold)
        write_results(result, args.output, args.format)
        print(f"已写入 {len(result)} 条高光候选：{args.output}")

        if args.video:
            manifest = export_highlights(
                args.video,
                result,
                platform=args.platform,
                output_dir=args.export_dir,
                ffmpeg=args.ffmpeg,
                layout=args.layout,
                crf=args.crf,
                execute=args.execute,
            )
            action = "完成导出" if args.execute else "生成导出命令"
            print(f"已为 {manifest['platform']['name']} {action}：{manifest['manifest_path']}")
    except (ValueError, FileNotFoundError, ClipExportError, json.JSONDecodeError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
