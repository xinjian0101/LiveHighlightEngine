# LiveHighlightEngine

本地优先的直播回放爆点分析与候选片段选择器。

## MVP

- 综合音频、弹幕、OCR、关键词四类信号评分
- 合并相邻候选片段
- 输出按得分排序的 JSON
- 无需付费 API

## 运行

```bash
python main.py examples/events.jsonl --threshold 0.45 --top 10 -o highlights.json
```

输入格式：每行一个 JSON 对象，包含 `start`、`end`，并可包含 `audio`、`danmaku`、`ocr`、`keyword`、`text`。

## 测试

```bash
python -m unittest -v
```

## License

MIT
