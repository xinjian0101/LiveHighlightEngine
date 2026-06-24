from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.core.platform_profiles import public_configuration
from backend.services.danmaku_parser import load_danmaku_events
from backend.services.local_highlight_engine import SignalEvent, select_highlights
from backend.utils.multiplatform_export import export_clips

router = APIRouter()


class AnalyzeRequest(BaseModel):
    events: list[dict[str, Any]]
    threshold: float = Field(default=0.45, ge=0, le=1)
    merge_gap_seconds: float = Field(default=5.0, ge=0, le=120)
    max_results: int = 10
    weights: dict[str, float] | None = None


class PipelineRequest(BaseModel):
    clean_video_path: str
    danmaku_path: str
    platform: str = "douyin"
    output_dir: str
    channel_mode: str = "danmaku_file"
    layout: str = "center"
    threshold: float = Field(default=0.45, ge=0, le=1)
    merge_gap_seconds: float = Field(default=5.0, ge=0, le=120)
    max_clips: int = 10
    danmaku_delay_seconds: float = 10.0
    execute: bool = False
    ffmpeg_path: str = "ffmpeg"


@router.get("/configuration")
def get_configuration() -> dict[str, Any]:
    return public_configuration()


@router.post("/analyze")
def analyze(request: AnalyzeRequest) -> dict[str, Any]:
    try:
        events = [SignalEvent(**item) for item in request.events]
        highlights = select_highlights(
            events,
            threshold=request.threshold,
            gap_seconds=request.merge_gap_seconds,
            max_results=request.max_results,
            weights=request.weights,
        )
        return {"count": len(highlights), "highlights": highlights}
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/run")
def run_pipeline(request: PipelineRequest) -> dict[str, Any]:
    try:
        clean = Path(request.clean_video_path)
        if clean.name.lower() != "clean.mp4":
            raise ValueError("最终导出只能从 clean.mp4 生成")
        if request.channel_mode not in ("ocr_video", "danmaku_file"):
            raise ValueError("未知分析通道")
        if request.channel_mode == "ocr_video":
            raise ValueError("OCR 视频通道已保留接口；当前压缩包先提供可直接运行的弹幕文件通道")
        raw_events = load_danmaku_events(
            request.danmaku_path,
            danmaku_delay_seconds=request.danmaku_delay_seconds,
        )
        highlights = select_highlights(
            [SignalEvent(**item) for item in raw_events],
            threshold=request.threshold,
            gap_seconds=request.merge_gap_seconds,
            max_results=request.max_clips,
        )
        manifest = export_clips(
            clean,
            highlights,
            platform=request.platform,
            output_dir=request.output_dir,
            layout=request.layout,
            ffmpeg_path=request.ffmpeg_path,
            max_clips=request.max_clips,
            execute=request.execute,
        )
        return {"highlights": highlights, "export": manifest}
    except (FileNotFoundError, RuntimeError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
