import unittest
import main


class EngineTest(unittest.TestCase):
    def test_score(self):
        item = main.Event(0, 2, danmaku=1.0, keyword=1.0)
        result = main.select([item], threshold=0.4)
        self.assertEqual(len(result), 1)


if __name__ == "__main__":
    unittest.main()
