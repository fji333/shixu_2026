from pathlib import Path
import sys
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.database import Base
from app.models import Category, ChatRecord, Feedback, KnowledgeDoc
from app.services import dashboard_service


class DashboardServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        self.SessionLocal = sessionmaker(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        self.db = self.SessionLocal()

        self.social_category = Category(name="社会保障", description="社保相关")
        self.medical_category = Category(name="医疗卫生", description="医保相关")
        self.db.add_all([self.social_category, self.medical_category])
        self.db.commit()
        self.db.refresh(self.social_category)
        self.db.refresh(self.medical_category)

        self.db.add_all(
            [
                KnowledgeDoc(
                    title="社保补贴政策",
                    category_id=self.social_category.id,
                    content="社保补贴政策正文",
                    status="active",
                ),
                KnowledgeDoc(
                    title="医保参保指南",
                    category_id=self.medical_category.id,
                    content="医保参保指南正文",
                    status="active",
                ),
                KnowledgeDoc(
                    title="草稿文档",
                    category_id=self.medical_category.id,
                    content="草稿正文",
                    status="draft",
                ),
            ]
        )
        self.db.commit()

        self.social_chat = ChatRecord(
            user_question="社保补贴怎么办？",
            ai_answer="社保补贴办理回答",
            category_id=self.social_category.id,
        )
        self.medical_chat = ChatRecord(
            user_question="医保怎么参保？",
            ai_answer="医保参保回答" * 30,
            category_id=self.medical_category.id,
        )
        self.db.add_all([self.social_chat, self.medical_chat])
        self.db.commit()
        self.db.refresh(self.social_chat)
        self.db.refresh(self.medical_chat)

        self.db.add_all(
            [
                Feedback(chat_id=self.social_chat.id, rating="helpful", comment="清楚"),
                Feedback(chat_id=self.medical_chat.id, rating="unhelpful", comment="不够细"),
                Feedback(chat_id=self.medical_chat.id, rating="neutral", comment=None),
            ]
        )
        self.db.commit()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_get_dashboard_data_returns_overview_and_recent_items(self):
        dashboard = dashboard_service.get_dashboard_data(self.db)

        self.assertEqual(dashboard.overview.total_knowledge_docs, 3)
        self.assertEqual(dashboard.overview.active_knowledge_docs, 2)
        self.assertEqual(dashboard.overview.total_chat_records, 2)
        self.assertEqual(dashboard.overview.total_feedback, 3)
        self.assertEqual(dashboard.overview.helpful_feedback, 1)
        self.assertEqual(dashboard.overview.unhelpful_feedback, 1)
        self.assertEqual(dashboard.overview.neutral_feedback, 1)

        statistics_by_name = {
            item.category_name: item
            for item in dashboard.category_statistics
        }
        self.assertEqual(statistics_by_name["社会保障"].chat_count, 1)
        self.assertEqual(statistics_by_name["社会保障"].knowledge_count, 1)
        self.assertEqual(statistics_by_name["医疗卫生"].chat_count, 1)
        self.assertEqual(statistics_by_name["医疗卫生"].knowledge_count, 2)

        self.assertEqual(len(dashboard.recent_chats), 2)
        self.assertLessEqual(len(dashboard.recent_chats[0].ai_answer), 153)
        self.assertEqual(len(dashboard.recent_feedback), 3)


if __name__ == "__main__":
    unittest.main()
