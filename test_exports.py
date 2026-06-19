import csv
import json
import tempfile
import unittest
from pathlib import Path

import main


class HighlightExportTest(unittest.TestCase):
    def setUp(self):
        self.items = [
            {
                "start": 10.0,
                "end": 25.0,
                "score": 0.8,
                "reasons": ["danmaku", "keyword"],
                "text": "Key moment",
            },
            {
                "start": 40.0,
                "end": 50.0,
                "score": 0.6,
                "reasons": ["audio"],
                "text": "Second moment",
            },
        ]

    def test_summary(self):
        summary = main.summarize_results(self.items)
        self.assertEqual(summary["count"], 2)
        self.assertEqual(summary["total_duration_seconds"], 25.0)
        self.assertEqual(summary["average_score"], 0.7)
        self.assertEqual(summary["reason_counts"]["keyword"], 1)

    def test_json_export_contains_summary(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            main.write_results(self.items, str(path), "json")
            value = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(value["summary"]["count"], 2)
        self.assertEqual(len(value["highlights"]), 2)

    def test_csv_export(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.csv"
            main.write_results(self.items, str(path), "csv")
            with path.open("r", encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
        self.assertEqual(rows[0]["duration"], "15.0")
        self.assertEqual(rows[0]["reasons"], "danmaku;keyword")

    def test_markdown_export(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.md"
            main.write_results(self.items, str(path), "markdown")
            content = path.read_text(encoding="utf-8")
        self.assertIn("# Highlight Report", content)
        self.assertIn("Key moment", content)

    def test_format_inference(self):
        self.assertEqual(main.infer_output_format("result.csv"), "csv")
        self.assertEqual(main.infer_output_format("result.md"), "markdown")
        self.assertEqual(main.infer_output_format("result.data"), "json")


if __name__ == "__main__":
    unittest.main()
