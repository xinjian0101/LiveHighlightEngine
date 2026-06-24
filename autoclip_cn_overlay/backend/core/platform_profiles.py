from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class PlatformProfile:
    key: str
    name: str
    width: int
    height: int
    fps: int
    video_bitrate: str
    audio_bitrate: str
    aspect_ratio: str
    min_duration: float
    max_duration: float
    safe_top: int = 0
    safe_bottom: int = 0
    safe_left: int = 0
    safe_right: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


PLATFORM_PROFILES: dict[str, PlatformProfile] = {
    "bilibili": PlatformProfile("bilibili", "B站", 1920, 1080, 30, "8M", "192k", "16:9", 5, 600, 48, 72, 48, 48),
    "douyin": PlatformProfile("douyin", "抖音", 1080, 1920, 30, "8M", "192k", "9:16", 5, 300, 180, 360, 64, 160),
    "tiktok": PlatformProfile("tiktok", "TikTok", 1080, 1920, 30, "8M", "192k", "9:16", 5, 600, 170, 340, 60, 150),
}

CLIP_COUNT_OPTIONS = (5, 10, 15, 20, 25, 30)
LAYOUT_OPTIONS = ("center", "fit", "blur")
CHANNEL_MODES = {
    "ocr_video": "纯净版 + 弹幕视频 OCR",
    "danmaku_file": "纯净版 + 弹幕文件",
}


def get_platform_profile(key: str) -> PlatformProfile:
    normalized = key.strip().lower()
    if normalized not in PLATFORM_PROFILES:
        raise ValueError(f"不支持的平台：{key}")
    return PLATFORM_PROFILES[normalized]


def public_configuration() -> dict[str, Any]:
    return {
        "platforms": {key: value.to_dict() for key, value in PLATFORM_PROFILES.items()},
        "clip_count_options": list(CLIP_COUNT_OPTIONS),
        "layout_options": list(LAYOUT_OPTIONS),
        "channel_modes": CHANNEL_MODES,
        "privacy_notice": "所有视频只在本机处理，最终切片只从 clean.mp4 导出。",
    }
