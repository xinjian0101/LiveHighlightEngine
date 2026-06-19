import json
import tempfile
import unittest
from pathlib import Path

import main


class EngineConfigurationTest(unittest.TestCase):
    def test_weights_are_normalized(self):
        weights = main.validate_weights({"audio": 1, "danmaku": 1, "ocr": 1, "keyword": 1})
        self.assertAlmostEqual(sum(weights.values()), 1.0)
        self.assertEqual(weights["audio"], 0.25)

    def test_invalid_event_is_rejected(self):
        with self.assertRaises(ValueError):
            main.validate_event(main.Event(start=4, end=3))

    def test_config_changes_selection(self):
        events = [main.Event(0, 2, audio=1.0)]
        result = main.select(
            events,
            threshold=0.4,
            weights={"audio": 1, "danmaku": 0, "ocr": 0, "keyword": 0},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["score"], 1.0)

    def test_load_events_accepts_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.jsonl"
            path.write_text(
                json.dumps({"start": 0, "end": 2, "source_id": "sample", "metadata": {"kind": "demo"}}) + "\n",
                encoding="utf-8",
            )
            events = main.load_events(str(path))
        self.assertEqual(events[0].source_id, "sample")
        self.assertEqual(events[0].metadata["kind"], "demo")


if __name__ == "__main__":
    unittest.main()
