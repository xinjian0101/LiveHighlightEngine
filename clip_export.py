from __future__ import annotations

import json
import shlex
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


@dataclass(frozen=True)
class PlatformPreset:
    key: str
    name: str
    width: int
    height: int
    fps: int
    video_bitrate: str
    audio_bitrate: str
    min_duration: float
    max_duration: float
    aspect_ratio: str
    container: str = "mp4"


PLATFORM_PRESETS: dict[str, PlatformPreset] = {
    "bilibili": PlatformPreset(
        key="bilibili",
        name="B站",
        width=1920,
        height=1080,
        fps=30,
        video_bitrate="8M",
        audio_bitrate="192k",
        min_duration=5.0,
        max_duration=600.0,
        aspect_ratio="16:9",
    ),
    "douyin": PlatformPreset(
        key="douyin",
        name="抖音",
        width=1080,
        height=1920,
        fps=30,
        video_bitrate="8M",
        audio_bitrate="192k",
        min_duration=5.0,
        max_duration=300.0,
        aspect_ratio="9:16",
    ),
    "tiktok": PlatformPreset(
        key="tiktok",
        name="TikTok",
        width=1080,
        height=1920,
        fps=30,
        video_bitrate="8M",
        audio_bitrate="192k",
        min_duration=5.0,
        max_duration=600.0,
        aspect_ratio="9:16",
    ),
}


class ClipExportError(RuntimeError):
    """Raised when a clip cannot be prepared or exported."""


def get_platform_preset(platform: str) -> PlatformPreset:
    key = platform.strip().lower()
    try:
        return PLATFORM_PRESETS[key]
    except KeyError as exc:
        choices = ", ".join(PLATFORM_PRESETS)
        raise ValueError(f"不支持的平台：{platform}。可选值：{choices}") from exc


def _validate_highlight(item: Mapping[str, Any]) -> tuple[float, float]:
    try:
        start = float(item["start"])
        end = float(item["end"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("切片数据必须包含有效的 start 和 end") from exc
    if start < 0 or end <= start:
        raise ValueError(f"无效切片区间：start={start}, end={end}")
    return start, end


def _fit_filter(preset: PlatformPreset) -> str:
    return (
        f"scale={preset.width}:{preset.height}:force_original_aspect_ratio=decrease,"
        f"pad={preset.width}:{preset.height}:(ow-iw)/2:(oh-ih)/2,"
        f"setsar=1,fps={preset.fps}"
    )


def _center_crop_filter(preset: PlatformPreset) -> str:
    return (
        f"scale={preset.width}:{preset.height}:force_original_aspect_ratio=increase,"
        f"crop={preset.width}:{preset.height},setsar=1,fps={preset.fps}"
    )


def build_video_filter(preset: PlatformPreset, layout: str) -> str:
    normalized = layout.strip().lower()
    if normalized == "fit":
        return _fit_filter(preset)
    if normalized == "center":
        return _center_crop_filter(preset)
    raise ValueError("layout 仅支持 center 或 fit")


def build_ffmpeg_command(
    video_path: str | Path,
    output_path: str | Path,
    highlight: Mapping[str, Any],
    preset: PlatformPreset,
    *,
    ffmpeg: str = "ffmpeg",
    layout: str = "center",
    crf: int = 20,
) -> list[str]:
    start, end = _validate_highlight(highlight)
    duration = end - start
    if duration < preset.min_duration:
        raise ValueError(
            f"切片时长 {duration:.2f}s 小于 {preset.name} 预设最短时长 {preset.min_duration:.2f}s"
        )
    if duration > preset.max_duration:
        raise ValueError(
            f"切片时长 {duration:.2f}s 超过 {preset.name} 预设最长时长 {preset.max_duration:.2f}s"
        )
    if not 0 <= crf <= 51:
        raise ValueError("CRF 必须在 0 到 51 之间")

    video_filter = build_video_filter(preset, layout)
    return [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-ss",
        f"{start:.3f}",
        "-i",
        str(video_path),
        "-t",
        f"{duration:.3f}",
        "-vf",
        video_filter,
        "-map",
        "0:v:0",
        "-map",
        "0:a?",
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        str(crf),
        "-maxrate",
        preset.video_bitrate,
        "-bufsize",
        preset.video_bitrate,
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        preset.audio_bitrate,
        "-ar",
        "48000",
        "-movflags",
        "+faststart",
        str(output_path),
    ]


def command_to_text(command: Sequence[str]) -> str:
    return shlex.join(command)


def export_highlights(
    video_path: str | Path,
    highlights: Iterable[Mapping[str, Any]],
    *,
    platform: str,
    output_dir: str | Path,
    ffmpeg: str = "ffmpeg",
    layout: str = "center",
    crf: int = 20,
    execute: bool = False,
) -> dict[str, Any]:
    source = Path(video_path)
    if execute and not source.is_file():
        raise FileNotFoundError(f"找不到源视频：{source}")

    preset = get_platform_preset(platform)
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    jobs: list[dict[str, Any]] = []
    for index, item in enumerate(highlights, 1):
        start, end = _validate_highlight(item)
        output_path = target_dir / f"{preset.key}_{index:02d}_{int(start):06d}-{int(end):06d}.{preset.container}"
        command = build_ffmpeg_command(
            source,
            output_path,
            item,
            preset,
            ffmpeg=ffmpeg,
            layout=layout,
            crf=crf,
        )
        status = "待执行"
        error: str | None = None
        if execute:
            try:
                subprocess.run(command, check=True)
                status = "已完成"
            except FileNotFoundError as exc:
                raise ClipExportError(f"找不到 FFmpeg 可执行文件：{ffmpeg}") from exc
            except subprocess.CalledProcessError as exc:
                status = "失败"
                error = f"FFmpeg 返回代码 {exc.returncode}"

        jobs.append(
            {
                "index": index,
                "platform": preset.key,
                "platform_name": preset.name,
                "aspect_ratio": preset.aspect_ratio,
                "start": start,
                "end": end,
                "duration": round(end - start, 3),
                "score": item.get("score"),
                "output": str(output_path),
                "status": status,
                "error": error,
                "command": command,
                "command_text": command_to_text(command),
            }
        )

    manifest = {
        "source_video": str(source),
        "platform": asdict(preset),
        "layout": layout,
        "execute": execute,
        "jobs": jobs,
    }
    manifest_path = target_dir / "export_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest["manifest_path"] = str(manifest_path)
    return manifest
