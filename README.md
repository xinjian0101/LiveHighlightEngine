# StreamClip CN｜多平台直播高光切片引擎

一个面向中文创作者的本地自动切片工具。它把音频峰值、弹幕热度、OCR 画面文字和关键词信号合并为可解释的高光评分，并可直接调用 FFmpeg 导出适配 **B站、抖音和 TikTok** 的视频片段。

> 当前版本：可用的命令行 MVP。支持高光筛选、平台预设、切片命令生成和 FFmpeg 实际导出；暂不包含自动登录或自动发布。

## 核心功能

- 完全本地运行，不上传源视频
- 音频、弹幕、OCR、关键词四信号加权评分
- 自动合并相邻高光，过滤低分片段
- 中文命令行、中文 Markdown/CSV 报告
- B站 16:9 导出预设
- 抖音 9:16 竖屏导出预设
- TikTok 9:16 竖屏导出预设
- 支持居中裁切与完整适配两种画面布局
- 支持只生成 FFmpeg 命令，也支持直接执行切片
- 每次导出生成 `export_manifest.json`，便于审核、重试和批处理

## 平台预设

| 平台 | 分辨率 | 比例 | 帧率 | 视频编码 | 音频编码 |
|---|---:|---:|---:|---|---|
| B站 | 1920×1080 | 16:9 | 30fps | H.264 | AAC 192k |
| 抖音 | 1080×1920 | 9:16 | 30fps | H.264 | AAC 192k |
| TikTok | 1080×1920 | 9:16 | 30fps | H.264 | AAC 192k |

## 环境

- Python 3.10+
- FFmpeg 6+（仅实际导出时需要）
- 无强制第三方 Python 依赖

## 快速开始

### 1. 准备高光信号

输入文件采用 JSONL，每行代表一个候选时间区间：

```json
{"start":12.0,"end":35.0,"audio":0.62,"danmaku":0.91,"ocr":0.35,"keyword":0.80,"text":"关键反转后弹幕爆发"}
```

字段说明：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| `start` | number | 是 | 开始时间，单位秒 |
| `end` | number | 是 | 结束时间，单位秒 |
| `audio` | number | 否 | 音频强度，0-1 |
| `danmaku` | number | 否 | 弹幕密度，0-1 |
| `ocr` | number | 否 | 画面文字变化，0-1 |
| `keyword` | number | 否 | 关键词命中强度，0-1 |
| `text` | string | 否 | 审核摘要 |

### 2. 只筛选高光

```bash
python main.py examples/events.jsonl --threshold 0.45 --top 10 -o highlights.json
```

### 3. 生成抖音切片命令

不加 `--execute` 时不会处理视频，只会生成可审核的 FFmpeg 命令清单：

```bash
python main.py examples/events.jsonl \
  --video input.mp4 \
  --platform douyin \
  --layout center \
  --export-dir exports/douyin
```

### 4. 实际导出抖音切片

```bash
python main.py examples/events.jsonl \
  --video input.mp4 \
  --platform douyin \
  --layout center \
  --export-dir exports/douyin \
  --execute
```

### 5. 导出 B站与 TikTok

```bash
# B站横屏
python main.py examples/events.jsonl --video input.mp4 --platform bilibili --layout fit --export-dir exports/bilibili --execute

# TikTok 竖屏
python main.py examples/events.jsonl --video input.mp4 --platform tiktok --layout center --export-dir exports/tiktok --execute
```

## 画面布局

- `center`：放大并居中裁切，适合抖音/TikTok 竖屏。可能裁掉画面边缘。
- `fit`：完整保留原画面，不足区域自动补边，适合 B站或需要保留游戏 UI 的内容。

## 输出结构

```text
exports/douyin/
├── douyin_01_000012-000035.mp4
├── douyin_02_000120-000165.mp4
└── export_manifest.json
```

清单记录平台参数、时间区间、输出文件、执行状态、错误信息和完整 FFmpeg 命令。

## 当前边界

- 不负责抓取无授权的视频
- 不自动登录、上传或发布到平台
- 不自动判断版权、隐私或平台合规性
- 当前竖屏采用居中裁切或完整适配，人物追踪重构列入后续版本
- 输入信号需要由弹幕解析、OCR、音频分析或字幕模块预先生成

## 下一阶段

1. 直接读取本地视频并自动提取音频峰值
2. 导入 B站弹幕 XML 与录屏弹幕画面
3. 集成本地 Whisper 生成中文字幕
4. 增加人物/主播追踪式 9:16 重构
5. 增加批量项目管理和 Web 中文界面
6. 增加平台标题、封面、安全区和发布清单

## 测试

```bash
python -m unittest discover -s tests -v
```

## 参考项目

- AutoClip：`zhouxiaoka/autoclip`，MIT License
- OpenShorts：`mutonby/openshorts`，MIT License

本仓库未直接复制上述项目代码，仅参考其产品方向和公开功能设计。

## License

MIT
