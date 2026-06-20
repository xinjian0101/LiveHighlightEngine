from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()


def replace_once(rel: str, old: str, new: str) -> None:
    path = ROOT / rel
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"patch marker not found in {rel}: {old[:80]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def insert_before(rel: str, marker: str, content: str) -> None:
    path = ROOT / rel
    text = path.read_text(encoding="utf-8")
    if marker not in text:
        raise RuntimeError(f"insert marker not found in {rel}: {marker!r}")
    path.write_text(text.replace(marker, content + "\n" + marker, 1), encoding="utf-8")


insert_before(
    "backend/api/v1/__init__.py",
    "# 注册所有路由",
    "from .local_clips import router as local_clips_router",
)
insert_before(
    "backend/api/v1/__init__.py",
    '__all__ = ["api_router"]',
    'api_router.include_router(local_clips_router, prefix="/local-clips", tags=["local-clips"])',
)

replace_once(
    "frontend/src/App.tsx",
    "import SettingsPage from './pages/SettingsPage'",
    "import SettingsPage from './pages/SettingsPage'\nimport LocalClipPage from './pages/LocalClipPage'",
)
replace_once(
    "frontend/src/App.tsx",
    '<Route path="/settings" element={<SettingsPage />} />',
    '<Route path="/settings" element={<SettingsPage />} />\n          <Route path="/local-clips" element={<LocalClipPage />} />',
)
replace_once(
    "frontend/src/components/Header.tsx",
    "import { SettingOutlined, ArrowLeftOutlined, BulbOutlined, MoonOutlined } from '@ant-design/icons'",
    "import { SettingOutlined, ArrowLeftOutlined, BulbOutlined, MoonOutlined, ScissorOutlined } from '@ant-design/icons'",
)
replace_once(
    "frontend/src/components/Header.tsx",
    "Auto<em style={{ fontStyle: 'italic' }}>Clip</em>",
    "Auto<em style={{ fontStyle: 'italic' }}>Clip</em><span style={{ fontSize: '12px', marginLeft: '8px', color: 'var(--ac-muted)' }}>CN Multi</span>",
)
insert_before(
    "frontend/src/components/Header.tsx",
    '        <Button\n          type="text"\n          icon={<SettingOutlined />}',
    '''        <Button
          type="text"
          icon={<ScissorOutlined />}
          onClick={() => navigate('/local-clips')}
          style={{ color: 'var(--ac-sub)', border: '1px solid var(--ac-line)', borderRadius: '999px', height: '36px', padding: '0 16px', background: 'var(--ac-card)' }}
        >
          本地切片
        </Button>''',
)

readme = ROOT / "README.md"
original = readme.read_text(encoding="utf-8")
banner = """# AutoClip CN Multi

> 基于 AutoClip MIT 项目扩展：新增 B站、抖音、TikTok 多平台本地直播切片、弹幕文件峰值分析、S/A/B/C 评分、最多 30 条批量导出与 clean.mp4 纯净源约束。

- 页面：`#/local-clips`
- 文档：`docs/AUTOCLIP_CN_MULTI_PLATFORM.md`
- 所有素材默认只在本机处理。

---

"""
readme.write_text(banner + original, encoding="utf-8")

manifest = {
    "base_repository": "zhouxiaoka/autoclip",
    "base_commit": "17100c05252b9a947ea1a857f8d0ea4f3af2317b",
    "edition": "AutoClip CN Multi",
    "platforms": ["bilibili", "douyin", "tiktok"],
    "clip_count_options": [5, 10, 15, 20, 25, 30],
}
(ROOT / "PATCH_MANIFEST.json").write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
print(f"AutoClip CN patch applied to {ROOT}")
