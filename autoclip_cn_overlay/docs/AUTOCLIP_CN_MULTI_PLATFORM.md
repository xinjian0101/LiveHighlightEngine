# AutoClip CN 多平台本地切片改造

本版本直接基于 AutoClip 原仓库扩展，保留原有项目、下载、字幕、AI 分析和合集功能，同时新增完全本地的直播切片路径。

## 已加入

- B站、抖音、TikTok 三平台预设
- 切片数量 5、10、15、20、25、30，最多30条
- S/A/B/C 高光分级
- 弹幕峰值、关键词、OCR、音频四信号接口
- B站 XML、JSON、JSONL、CSV 弹幕解析
- 默认减去10秒弹幕延迟
- 最终只从 clean.mp4 导出
- 居中裁切、完整画面补边、模糊背景
- FFmpeg失败重试、导出清单和错误记录
- 本地处理，不强制上传素材

## 两条通道

1. 纯净版 + 弹幕文件：当前可直接运行。
2. 纯净版 + 弹幕视频 OCR：保留界面和接口，OCR事件提取器为后续迭代项。

## 页面

启动后访问 `#/local-clips`。

## API

- `GET /api/v1/local-clips/configuration`
- `POST /api/v1/local-clips/analyze`
- `POST /api/v1/local-clips/run`

## 合规

只处理你有权使用的视频、直播回放和弹幕数据。本项目不绕过平台授权，不包含未经授权的搬运发布功能。
