"""Project self-check script for the government Q&A system.

Run from the project root:
    python scripts/check_project.py
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from typing import Any
from urllib import error, request


DEFAULT_BASE_URL = "http://127.0.0.1:8000"
TIMEOUT_SECONDS = 8
CHAT_QUESTION = "医保报销需要哪些材料？"


@dataclass
class CheckResult:
    level: str
    name: str
    ok: bool
    message: str = ""
    reason: str = ""
    suggestion: str = ""
    critical: bool = False


def fetch_json(
    base_url: str,
    method: str,
    path: str,
    payload: dict[str, Any] | None = None,
) -> Any:
    url = f"{base_url.rstrip('/')}{path}"
    data = None
    headers = {"Accept": "application/json"}

    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"

    http_request = request.Request(url, data=data, headers=headers, method=method)
    with request.urlopen(http_request, timeout=TIMEOUT_SECONDS) as response:
        raw_body = response.read().decode("utf-8")
        if not raw_body:
            return {}
        return json.loads(raw_body)


def format_exception(exc: Exception) -> str:
    if isinstance(exc, error.HTTPError):
        try:
            body = exc.read().decode("utf-8")
        except Exception:
            body = ""
        if body:
            return f"HTTP {exc.code}: {body}"
        return f"HTTP {exc.code}: {exc.reason}"
    if isinstance(exc, error.URLError):
        return str(exc.reason)
    return str(exc)


def pass_result(name: str, message: str) -> CheckResult:
    return CheckResult("通过", name, ok=True, message=message)


def warn_result(name: str, message: str, suggestion: str = "") -> CheckResult:
    return CheckResult("提示", name, ok=True, message=message, suggestion=suggestion)


def fail_result(
    name: str,
    reason: str,
    suggestion: str,
    *,
    critical: bool = True,
) -> CheckResult:
    return CheckResult(
        "失败",
        name,
        ok=False,
        reason=reason,
        suggestion=suggestion,
        critical=critical,
    )


def list_count(value: Any) -> int:
    if isinstance(value, list):
        return len(value)
    if isinstance(value, dict):
        for key in ("items", "data", "results", "records"):
            if isinstance(value.get(key), list):
                return len(value[key])
    return 0


def evaluate_health(data: Any) -> CheckResult:
    if isinstance(data, dict) and data.get("status") == "ok":
        return pass_result("后端健康检查", "后端服务运行正常")
    if data:
        return pass_result("后端健康检查", "后端接口已正常响应")
    return fail_result(
        "后端健康检查",
        "接口未返回有效内容",
        "请先运行 uvicorn app.main:app --reload",
    )


def evaluate_database_ping(data: Any) -> CheckResult:
    if data:
        return pass_result("数据库连接", "数据库连接接口正常响应")
    return fail_result(
        "数据库连接",
        "接口未返回有效内容",
        "请检查 MySQL 服务和 .env 中 DATABASE_URL",
    )


def evaluate_categories(data: Any) -> CheckResult:
    count = list_count(data)
    if count > 0:
        return pass_result("政务分类接口", f"当前分类数量：{count}")
    return fail_result(
        "政务分类接口",
        "分类列表为空",
        "请运行 python scripts/seed_categories.py 初始化默认政务分类",
    )


def evaluate_knowledge(data: Any) -> CheckResult:
    count = list_count(data)
    if count > 0:
        return pass_result("知识库接口", f"当前文档数量：{count}")
    return warn_result(
        "知识库接口",
        "知识库为空",
        "请运行 python scripts/import_knowledge.py 或通过前端新增文档",
    )


def evaluate_vector_status(data: Any) -> CheckResult:
    chunk_count = int(data.get("chunk_count") or 0) if isinstance(data, dict) else 0
    vector_count = int(data.get("vector_count") or 0) if isinstance(data, dict) else 0
    message = f"chunks：{chunk_count}，vectors：{vector_count}"
    if chunk_count == 0 or vector_count == 0:
        return warn_result(
            "向量索引状态",
            message,
            "建议运行 python scripts/build_vector_index.py",
        )
    return pass_result("向量索引状态", message)


def evaluate_llm_status(data: Any) -> CheckResult:
    enabled = bool(data.get("enabled")) if isinstance(data, dict) else False
    available = bool(data.get("available")) if isinstance(data, dict) else False
    if not enabled or not available:
        return pass_result(
            "大模型预留状态",
            "当前为大模型预留模式，未启用真实 API",
        )
    provider = data.get("provider") or "已配置服务商"
    model = data.get("model") or "已配置模型"
    return pass_result("大模型预留状态", f"当前配置：{provider} / {model}")


def evaluate_dashboard(data: Any) -> CheckResult:
    if isinstance(data, dict) and isinstance(data.get("overview"), dict):
        return pass_result("数据看板接口", "overview 字段正常返回")
    return fail_result(
        "数据看板接口",
        "响应中缺少 overview 字段",
        "请检查后端 /dashboard 接口和数据库统计数据",
    )


def evaluate_chat_response(data: Any) -> CheckResult:
    required_fields = ("ai_answer", "retrieval_mode", "answer_mode")
    missing = [field for field in required_fields if field not in data]
    if missing:
        return fail_result(
            "RAG 问答接口",
            f"响应中缺少字段：{', '.join(missing)}",
            "请检查 /chat 接口响应结构",
        )

    answer_mode = data.get("answer_mode") or "未知"
    retrieval_mode = data.get("retrieval_mode") or "未知"
    reference_count = data.get("reference_count")
    message = f"回答模式：{answer_mode}，检索方式：{retrieval_mode}"
    if reference_count is not None:
        message = f"{message}，参考依据数量：{reference_count}"
    elif "references" in data:
        message = f"{message}，已返回参考依据列表"
    return pass_result("RAG 问答接口", message)


def run_endpoint_check(
    base_url: str,
    method: str,
    path: str,
    evaluator,
    *,
    payload: dict[str, Any] | None = None,
    failure_name: str,
    failure_suggestion: str,
    critical: bool = True,
) -> CheckResult:
    try:
        data = fetch_json(base_url, method, path, payload)
        return evaluator(data)
    except Exception as exc:
        return fail_result(
            failure_name,
            format_exception(exc),
            failure_suggestion,
            critical=critical,
        )


def run_checks(base_url: str) -> list[CheckResult]:
    return [
        run_endpoint_check(
            base_url,
            "GET",
            "/health",
            evaluate_health,
            failure_name="后端健康检查",
            failure_suggestion="请先运行 uvicorn app.main:app --reload",
        ),
        run_endpoint_check(
            base_url,
            "GET",
            "/database/ping",
            evaluate_database_ping,
            failure_name="数据库连接",
            failure_suggestion="请检查 MySQL 服务和 .env 中 DATABASE_URL",
        ),
        run_endpoint_check(
            base_url,
            "GET",
            "/categories",
            evaluate_categories,
            failure_name="政务分类接口",
            failure_suggestion="请运行 python scripts/seed_categories.py 初始化默认政务分类",
        ),
        run_endpoint_check(
            base_url,
            "GET",
            "/knowledge",
            evaluate_knowledge,
            failure_name="知识库接口",
            failure_suggestion="请运行 python scripts/import_knowledge.py 或通过前端新增文档",
            critical=False,
        ),
        run_endpoint_check(
            base_url,
            "GET",
            "/vector/status",
            evaluate_vector_status,
            failure_name="向量索引状态",
            failure_suggestion="请检查 /vector/status 接口；如索引为空，请运行 python scripts/build_vector_index.py",
            critical=False,
        ),
        run_endpoint_check(
            base_url,
            "GET",
            "/llm/status",
            evaluate_llm_status,
            failure_name="大模型预留状态",
            failure_suggestion="当前不需要真实 API Key；请检查 /llm/status 接口是否注册",
            critical=False,
        ),
        run_endpoint_check(
            base_url,
            "GET",
            "/dashboard",
            evaluate_dashboard,
            failure_name="数据看板接口",
            failure_suggestion="请检查后端 /dashboard 接口和数据库统计数据",
        ),
        run_endpoint_check(
            base_url,
            "POST",
            "/chat",
            evaluate_chat_response,
            payload={"question": CHAT_QUESTION},
            failure_name="RAG 问答接口",
            failure_suggestion=(
                "请确认后端已启动、数据库可用，并可用 Swagger 测试 POST /chat；"
                f"测试问题：{CHAT_QUESTION}"
            ),
        ),
    ]


def summarize_results(results: list[CheckResult]) -> dict[str, int]:
    return {
        "passed": sum(1 for item in results if item.level == "通过"),
        "failed": sum(1 for item in results if item.level == "失败"),
        "warnings": sum(1 for item in results if item.level == "提示"),
    }


def print_result(result: CheckResult) -> None:
    if result.level == "失败":
        print(f"[失败] {result.name}")
        print(f"失败原因：{result.reason}")
        print(f"建议处理：{result.suggestion}")
        return

    print(f"[{result.level}] {result.name}，{result.message}")
    if result.suggestion:
        print(f"建议处理：{result.suggestion}")


def print_report(base_url: str, results: list[CheckResult]) -> None:
    print("=" * 30)
    print("政务智能问答系统项目检查")
    print(f"后端地址：{base_url}")
    print("=" * 30)
    print()
    for result in results:
        print_result(result)
    print()
    summary = summarize_results(results)
    print("=" * 30)
    print(
        "检查完成："
        f"{summary['passed']} 项通过，"
        f"{summary['failed']} 项失败，"
        f"{summary['warnings']} 项提示"
    )
    print("=" * 30)


def has_critical_failure(results: list[CheckResult]) -> bool:
    return any((not item.ok) and item.critical for item in results)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="政务智能问答系统项目一键检查脚本")
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"后端服务地址，默认：{DEFAULT_BASE_URL}",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    results = run_checks(args.base_url)
    print_report(args.base_url, results)
    return 1 if has_critical_failure(results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
