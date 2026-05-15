from pathlib import Path
import sys
import unittest


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.config import settings
from app.services import llm_service


class LlmServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.original_values = {
            "llm_enable": settings.llm_enable,
            "llm_provider": settings.llm_provider,
            "llm_api_key": settings.llm_api_key,
            "llm_base_url": settings.llm_base_url,
            "llm_model": settings.llm_model,
        }

    def tearDown(self):
        for key, value in self.original_values.items():
            setattr(settings, key, value)

    def test_is_llm_available_requires_all_config(self):
        settings.llm_enable = True
        settings.llm_provider = "deepseek"
        settings.llm_api_key = ""
        settings.llm_base_url = "https://api.example.com"
        settings.llm_model = "demo-model"

        self.assertFalse(llm_service.is_llm_available())

    def test_generate_answer_returns_fallback_when_disabled(self):
        settings.llm_enable = False
        settings.llm_provider = ""
        settings.llm_api_key = ""
        settings.llm_base_url = ""
        settings.llm_model = ""

        result = llm_service.generate_answer_with_llm(
            "医保报销需要哪些材料？",
            [{"title": "医保报销材料指南", "content": "需要身份证和医保卡。"}],
        )

        self.assertFalse(result["success"])
        self.assertIsNone(result["answer"])
        self.assertIsNone(result["provider"])
        self.assertIsNone(result["model"])
        self.assertEqual(result["error"], "大模型未启用或未配置，已使用模板式 RAG 回答")

    def test_build_prompt_limits_answer_to_references(self):
        prompt = llm_service.build_government_rag_prompt(
            "医保报销需要哪些材料？",
            [{"title": "医保报销材料指南", "content": "需要身份证和医保卡。"}],
            safety_warning="请勿提交完整身份证号。",
        )

        self.assertIn("政务服务智能问答助手", prompt)
        self.assertIn("只能基于检索到的政策资料回答", prompt)
        self.assertIn("资料不足时不能编造", prompt)
        self.assertIn("请勿提交完整身份证号", prompt)


if __name__ == "__main__":
    unittest.main()
