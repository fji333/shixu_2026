from pathlib import Path
import shutil
import sys
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.config import PROJECT_ROOT, settings
from app.database import Base
from app.models import Category, KnowledgeChunk, KnowledgeDoc
from app.services import vector_service


class VectorServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.original_vector_db_path = settings.vector_db_path
        self.temp_dir = PROJECT_ROOT / "data" / "vector_db" / "test_vector_service"
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        settings.vector_db_path = self.temp_dir

        self.engine = create_engine("sqlite:///:memory:")
        self.SessionLocal = sessionmaker(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        self.db = self.SessionLocal()

        category = Category(name="医疗卫生", description="医保相关")
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)

        self.db.add(
            KnowledgeDoc(
                title="医保报销材料指南",
                category_id=category.id,
                content="办理医保报销通常需要身份证、医保卡、费用清单和医院票据。",
                source="测试文档",
                status="active",
            )
        )
        self.db.commit()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()
        settings.vector_db_path = self.original_vector_db_path
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_rebuild_vector_index_and_search_chunks(self):
        result = vector_service.rebuild_vector_index(self.db)

        self.assertEqual(result.document_count, 1)
        self.assertEqual(result.chunk_count, 1)
        self.assertEqual(result.vector_count, 1)
        self.assertEqual(self.db.query(KnowledgeChunk).count(), 1)

        search_result = vector_service.search_similar_chunks("医保报销需要哪些材料", limit=5)

        self.assertEqual(search_result.total, 1)
        self.assertEqual(search_result.results[0].title, "医保报销材料指南")
        self.assertIn("医保", search_result.results[0].content)


if __name__ == "__main__":
    unittest.main()
