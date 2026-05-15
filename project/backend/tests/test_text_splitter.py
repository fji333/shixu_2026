from pathlib import Path
import sys
import unittest


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.services.text_splitter import split_text


class TextSplitterTestCase(unittest.TestCase):
    def test_short_text_returns_single_chunk(self):
        chunks = split_text("城乡居民医保参保指南。", chunk_size=500, overlap=80)

        self.assertEqual(chunks, ["城乡居民医保参保指南。"])

    def test_long_text_is_split_with_overlap(self):
        text = "\n\n".join(
            [
                "第一段" + "社保政策" * 80,
                "第二段" + "办理材料" * 80,
                "第三段" + "窗口咨询" * 80,
            ]
        )

        chunks = split_text(text, chunk_size=120, overlap=30)

        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(chunk.strip() for chunk in chunks))
        self.assertTrue(all(len(chunk) <= 150 for chunk in chunks))
        self.assertIn(chunks[0][-30:], chunks[1])


if __name__ == "__main__":
    unittest.main()
