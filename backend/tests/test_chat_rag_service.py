from pathlib import Path
import sys
import unittest
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.database import Base
from app.models import Category, ChatRecord, KnowledgeDoc
from app.schemas.vector import VectorSearchItem, VectorSearchResponse
from app.services import chat_service


class ChatRagServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        self.SessionLocal = sessionmaker(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        self.db = self.SessionLocal()

        self.category = Category(name="医疗卫生", description="医保相关")
        self.db.add(self.category)
        self.db.commit()
        self.db.refresh(self.category)

        self.doc = KnowledgeDoc(
            title="医保报销材料指南",
            category_id=self.category.id,
            content="医保报销需要身份证、医保卡、费用清单和医院票据。",
            source="本地示例政策文档",
            status="active",
        )
        self.db.add(self.doc)
        self.db.commit()
        self.db.refresh(self.doc)

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_answer_question_prefers_vector_retrieval(self):
        vector_response = VectorSearchResponse(
            query="医保报销需要哪些材料？",
            total=1,
            results=[
                VectorSearchItem(
                    document_id=self.doc.id,
                    title=self.doc.title,
                    chunk_index=0,
                    content="医保报销需要身份证、医保卡、费用清单和医院票据。",
                    distance=0.12,
                    metadata={
                        "source": "本地示例政策文档",
                        "category_id": self.category.id,
                    },
                )
            ],
        )

        with patch(
            "app.services.chat_service.vector_service.search_similar_chunks",
            return_value=vector_response,
        ):
            record = chat_service.answer_question("医保报销需要哪些材料？", self.db)

        self.assertEqual(record.retrieval_mode, "vector")
        self.assertEqual(record.reference_count, 1)
        self.assertEqual(record.references[0]["title"], self.doc.title)
        self.assertEqual(record.answer_mode, "template_rag")
        self.assertEqual(record.llm_error, "大模型未启用或未配置，已使用模板式 RAG 回答")
        self.assertIn("[参考资料 1]", record.retrieved_context)
        self.assertIn("一、相关政策依据", record.ai_answer)
        self.assertEqual(self.db.query(ChatRecord).count(), 1)

    def test_answer_question_falls_back_to_keyword_retrieval(self):
        empty_vector_response = VectorSearchResponse(
            query="医保报销需要哪些材料？",
            total=0,
            results=[],
            message="向量索引为空",
        )

        with patch(
            "app.services.chat_service.vector_service.search_similar_chunks",
            return_value=empty_vector_response,
        ):
            record = chat_service.answer_question("医保报销需要哪些材料？", self.db)

        self.assertEqual(record.retrieval_mode, "keyword")
        self.assertEqual(record.reference_count, 1)
        self.assertEqual(record.references[0]["source"], "本地示例政策文档")

    def test_answer_question_keeps_sensitive_info_masked(self):
        empty_vector_response = VectorSearchResponse(
            query="我的手机号是13812345678，医保报销需要哪些材料？",
            total=0,
            results=[],
        )

        with patch(
            "app.services.chat_service.vector_service.search_similar_chunks",
            return_value=empty_vector_response,
        ):
            record = chat_service.answer_question(
                "我的手机号是13812345678，医保报销需要哪些材料？",
                self.db,
            )

        saved_record = self.db.query(ChatRecord).first()
        self.assertNotIn("13812345678", saved_record.user_question)
        self.assertEqual(record.masked_question, saved_record.user_question)
        self.assertTrue(record.has_sensitive_info)


if __name__ == "__main__":
    unittest.main()
