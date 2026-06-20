from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from clip_export import build_ffmpeg_command, export_highlights, get_platform_preset


class PlatformPresetTests(unittest.TestCase):
    def test_douyin_is_vertical(self) -> None:
        preset = get_platform_preset("douyin")
        self.assertEqual((preset.width, preset.height), (1080, 1920))
        self.assertEqual(preset.aspect_ratio, "9:16")

    def test_bilibili_is_landscape(self) -> None:
        preset = get_platform_preset("bilibili")
        self.assertEqual((preset.width, preset.height), (1920, 1080))
        self.assertEqual(preset.aspect_ratio, "16:9")

    def test_unknown_platform_rejected(self) -> None:
        with self.assertRaises(ValueError):
            get_platform_preset("unknown")


class CommandTests(unittest.TestCase):
    def test_build_vertical_command(self) -> None:
        command = build_ffmpeg_command(
            "input.mp4",
            "output.mp4",
            {"start": 10, "end": 40},
            get_platform_preset("tiktok"),
        )
        text = " ".join(command)
        self.assertIn("crop=1080:1920", text)
        self.assertIn("-t 30.000", text)
        self.assertEqual(command[-1], "output.mp4")

    def test_short_clip_rejected(self) -> None:
        with self.assertRaises(ValueError):
            build_ffmpeg_command(
                "input.mp4",
                "output.mp4",
                {"start": 1, "end": 3},
                get_platform_preset("douyin"),
            )

    def test_dry_run_writes_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest = export_highlights(
                "missing-but-allowed-in-dry-run.mp4",
                [{"start": 12, "end": 32, "score": 0.9}],
                platform="douyin",
                output_dir=temp_dir,
                execute=False,
            )
            self.assertEqual(manifest["jobs"][0]["status"], "待执行")
            self.assertTrue(Path(manifest["manifest_path"]).is_file())


if __name__ == "__main__":
    unittest.main()
