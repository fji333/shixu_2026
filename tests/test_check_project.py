import sys
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from scripts import check_project


class CheckProjectTestCase(unittest.TestCase):
    def test_vector_status_with_empty_index_is_warning_not_failure(self):
        result = check_project.evaluate_vector_status(
            {"chunk_count": 0, "vector_count": 0}
        )

        self.assertTrue(result.ok)
        self.assertEqual(result.level, "提示")
        self.assertIn("build_vector_index.py", result.suggestion)

    def test_llm_disabled_status_is_success(self):
        result = check_project.evaluate_llm_status(
            {"enabled": False, "available": False}
        )

        self.assertTrue(result.ok)
        self.assertEqual(result.level, "通过")
        self.assertIn("未启用真实 API", result.message)

    def test_chat_response_requires_core_fields(self):
        result = check_project.evaluate_chat_response({"ai_answer": "答复"})

        self.assertFalse(result.ok)
        self.assertEqual(result.level, "失败")
        self.assertIn("retrieval_mode", result.reason)

    def test_summary_counts_pass_fail_and_warning(self):
        results = [
            check_project.CheckResult("通过", "健康检查", ok=True),
            check_project.CheckResult("提示", "向量索引为空", ok=True),
            check_project.CheckResult("失败", "问答接口", ok=False),
        ]

        summary = check_project.summarize_results(results)

        self.assertEqual(summary["passed"], 1)
        self.assertEqual(summary["failed"], 1)
        self.assertEqual(summary["warnings"], 1)


if __name__ == "__main__":
    unittest.main()
