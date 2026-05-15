"""Import local sample policy documents into knowledge_docs.

This script imports each Markdown file in data/policies as one knowledge
document. It does not split text, build vectors, or write to Chroma.
"""

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"
POLICY_DIR = PROJECT_ROOT / "data" / "policies"
sys.path.insert(0, str(BACKEND_DIR))


def match_category_name(title: str) -> str:
    if "就业" in title or "创业" in title:
        return "就业创业"
    if "医保" in title or "医疗" in title:
        return "医疗卫生"
    if "居住证" in title:
        return "其他咨询"
    if "公积金" in title or "住房" in title:
        return "住房保障"
    if "城市管理" in title or "投诉" in title:
        return "城市管理"
    return "其他咨询"


def main() -> None:
    try:
        from sqlalchemy.exc import SQLAlchemyError

        from app.database import SessionLocal
        from app.models import Category, KnowledgeDoc
    except ModuleNotFoundError as exc:
        print(f"知识文档导入失败：缺少依赖 {exc.name}，请先安装 backend/requirements.txt")
        raise SystemExit(1) from exc

    if not POLICY_DIR.exists():
        print(f"知识文档导入失败：目录不存在 {POLICY_DIR}")
        raise SystemExit(1)

    imported_count = 0
    skipped_count = 0

    db = SessionLocal()
    try:
        for file_path in sorted(POLICY_DIR.glob("*.md")):
            title = file_path.stem
            exists = db.query(KnowledgeDoc).filter(KnowledgeDoc.title == title).first()
            if exists:
                skipped_count += 1
                continue

            category_name = match_category_name(title)
            category = db.query(Category).filter(Category.name == category_name).first()
            content = file_path.read_text(encoding="utf-8").strip()

            db.add(
                KnowledgeDoc(
                    title=title,
                    content=content,
                    source="本地示例政策文档",
                    category_id=category.id if category else None,
                    status="active",
                )
            )
            imported_count += 1

        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        print(f"知识文档导入失败：请检查数据库连接和表结构。错误：{exc}")
        raise SystemExit(1) from exc
    finally:
        db.close()

    print(f"知识文档导入完成，导入 {imported_count} 条，跳过 {skipped_count} 条")


if __name__ == "__main__":
    main()
