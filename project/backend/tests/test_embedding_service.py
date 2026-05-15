from pathlib import Path
import sys
import unittest


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.services.embedding_service import EMBEDDING_DIMENSION, embed_text, embed_texts


class EmbeddingServiceTestCase(unittest.TestCase):
    def test_embed_text_is_stable_and_fixed_dimension(self):
        first = embed_text("医保报销需要哪些材料")
        second = embed_text("医保报销需要哪些材料")

        self.assertEqual(len(first), EMBEDDING_DIMENSION)
        self.assertEqual(first, second)
        self.assertAlmostEqual(sum(value * value for value in first), 1.0, places=5)

    def test_related_chinese_texts_share_nonzero_signal(self):
        query = embed_text("医保报销材料")
        related = embed_text("办理医保报销需要准备材料")

        dot_product = sum(left * right for left, right in zip(query, related))

        self.assertGreater(dot_product, 0)

    def test_embed_texts_embeds_each_text(self):
        embeddings = embed_texts(["社保补贴", "医保参保"])

        self.assertEqual(len(embeddings), 2)
        self.assertTrue(all(len(item) == EMBEDDING_DIMENSION for item in embeddings))


if __name__ == "__main__":
    unittest.main()
