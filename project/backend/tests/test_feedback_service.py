from pathlib import Path
import sys
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.database import Base
from app.models import ChatRecord
from app.schemas.feedback import FeedbackCreate
from app.services import feedback_service


class FeedbackServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        self.SessionLocal = sessionmaker(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        self.db = self.SessionLocal()

        self.chat_record = ChatRecord(
            user_question="医保怎么参保？",
            ai_answer="请参考当地医保参保政策。",
        )
        self.db.add(self.chat_record)
        self.db.commit()
        self.db.refresh(self.chat_record)

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_create_feedback_for_existing_chat_record(self):
        feedback = feedback_service.create_feedback(
            self.db,
            FeedbackCreate(
                chat_id=self.chat_record.id,
                rating="helpful",
                comment="回答很清楚",
            ),
        )

        self.assertEqual(feedback.chat_id, self.chat_record.id)
        self.assertEqual(feedback.rating, "helpful")
        self.assertEqual(feedback.comment, "回答很清楚")

    def test_create_feedback_rejects_missing_chat_record(self):
        with self.assertRaises(ValueError) as context:
            feedback_service.create_feedback(
                self.db,
                FeedbackCreate(
                    chat_id=999,
                    rating="unhelpful",
                    comment="没有找到对应政策",
                ),
            )

        self.assertEqual(str(context.exception), "问答记录不存在，无法提交反馈")

    def test_get_feedback_statistics_counts_each_rating(self):
        for rating in ["helpful", "helpful", "unhelpful", "neutral"]:
            feedback_service.create_feedback(
                self.db,
                FeedbackCreate(
                    chat_id=self.chat_record.id,
                    rating=rating,
                    comment=None,
                ),
            )

        statistics = feedback_service.get_feedback_statistics(self.db)

        self.assertEqual(statistics.total, 4)
        self.assertEqual(statistics.helpful_count, 2)
        self.assertEqual(statistics.unhelpful_count, 1)
        self.assertEqual(statistics.neutral_count, 1)


if __name__ == "__main__":
    unittest.main()
