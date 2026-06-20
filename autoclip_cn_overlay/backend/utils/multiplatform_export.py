from __future__ import annotations

import json
import shlex
import subprocess
import time
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

from backend.core.platform_profiles import get_platform_profile

ProgressCallback = Callable[[int, int, str], None]


def _filter(platform: str, layout: str) -> str:
    profile = get_platform_profile(platform)
    width, height = profile.width, profile.height
    if layout == "fit":
        return f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={profile.fps}"
    if layout == "blur":
        return f"[0:v]scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},boxblur=24:8[bg];[0:v]scale={width}:{height}:force_original_aspect_ratio=decrease[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1,fps={profile.fps}[v]"
    if layout == "center":
        return f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},setsar=1,fps={profile.fps}"
    raise ValueError("layout 仅支持 center、fit、blur")


def build_command(clean_video_path: str | Path, output_path: str | Path, highlight: Mapping[str, Any], *, platform: str, layout: str = "center", ffmpeg_path: str = "ffmpeg", crf: int = 20) -> list[str]:
    start, end = float(highlight["start"]), float(highlight["end"])
    duration = end - start
    profile = get_platform_profile(platform)
    if start < 0 or duration <= 0:
        raise ValueError("切片时间区间无效")
    if duration < profile.min_duration or duration > profile.max_duration:
        raise ValueError(f"切片时长 {duration:.2f}s 不符合 {profile.name} 预设")
    if not 0 <= crf <= 51:
        raise ValueError("CRF 必须在 0 到 51 之间")
    video_filter = _filter(platform, layout)
    command = [ffmpeg_path, "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{start:.3f}", "-i", str(clean_video_path), "-t", f"{duration:.3f}"]
    command.extend(["-filter_complex" if layout == "blur" else "-vf", video_filter])
    command.extend(["-map", "[v]" if layout == "blur" else "0:v:0", "-map", "0:a?", "-c:v", "libx264", "-preset", "fast", "-crf", str(crf), "-maxrate", profile.video_bitrate, "-bufsize", profile.video_bitrate, "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", profile.audio_bitrate, "-ar", "48000", "-movflags", "+faststart", str(output_path)])
    return command


def export_clips(clean_video_path: str | Path, highlights: Iterable[Mapping[str, Any]], *, platform: str, output_dir: str | Path, layout: str = "center", ffmpeg_path: str = "ffmpeg", crf: int = 20, max_clips: int = 10, execute: bool = True, retries: int = 2, progress: ProgressCallback | None = None) -> dict[str, Any]:
    source = Path(clean_video_path)
    if source.name.lower() != "clean.mp4":
        raise ValueError("最终导出只能使用名为 clean.mp4 的纯净版视频")
    if execute and not source.is_file():
        raise FileNotFoundError(f"找不到纯净版视频：{source}")
    if max_clips not in (5, 10, 15, 20, 25, 30):
        raise ValueError("切片数量只能是 5、10、15、20、25、30")
    profile = get_platform_profile(platform)
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    selected = list(highlights)[:max_clips]
    jobs: list[dict[str, Any]] = []
    for index, item in enumerate(selected, 1):
        start, end = float(item["start"]), float(item["end"])
        output = target / f"{profile.key}_{index:02d}_{int(start):06d}-{int(end):06d}.mp4"
        command = build_command(source, output, item, platform=platform, layout=layout, ffmpeg_path=ffmpeg_path, crf=crf)
        state, error = "待执行", None
        if execute:
            for attempt in range(retries + 1):
                if progress:
                    progress(index, len(selected), f"正在导出 {output.name}，第 {attempt + 1} 次尝试")
                try:
                    subprocess.run(command, check=True, capture_output=True, text=True)
                    state = "已完成"
                    break
                except FileNotFoundError as exc:
                    raise RuntimeError(f"找不到 FFmpeg：{ffmpeg_path}") from exc
                except subprocess.CalledProcessError as exc:
                    error = (exc.stderr or str(exc))[-2000:]
                    state = "失败"
                    if attempt < retries:
                        time.sleep(1.5 * (attempt + 1))
        jobs.append({"index": index, "grade": item.get("grade"), "score": item.get("score"), "start": start, "end": end, "output": str(output), "status": state, "error": error, "command": command, "command_text": shlex.join(command)})
    manifest = {"source": str(source), "platform": profile.to_dict(), "layout": layout, "max_clips": max_clips, "execute": execute, "jobs": jobs}
    manifest_path = target / "export_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest["manifest_path"] = str(manifest_path)
    return manifest
