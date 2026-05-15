"""Seed default government service categories."""

from pathlib import Path
import sys


BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND_DIR))


DEFAULT_CATEGORIES = [
    ("社会保障", "社会保险、养老服务、救助保障等咨询分类"),
    ("医疗卫生", "医保参保、医疗服务、公共卫生等咨询分类"),
    ("教育服务", "入学、资助、考试、继续教育等咨询分类"),
    ("就业创业", "就业服务、创业扶持、补贴申领等咨询分类"),
    ("住房保障", "公租房、住房补贴、公积金等咨询分类"),
    ("交通出行", "公共交通、车辆业务、出行服务等咨询分类"),
    ("市场监管", "经营主体、消费维权、食品安全等咨询分类"),
    ("城市管理", "市容环境、投诉处理、便民服务等咨询分类"),
    ("公共安全", "安全生产、应急管理、治安服务等咨询分类"),
    ("其他咨询", "无法归入以上分类的综合咨询"),
]


def main() -> None:
    try:
        from sqlalchemy.exc import SQLAlchemyError

        from app.database import SessionLocal
        from app.models import Category
    except ModuleNotFoundError as exc:
        print(f"默认分类初始化失败：缺少依赖 {exc.name}，请先安装 backend/requirements.txt")
        raise SystemExit(1) from exc

    created_count = 0
    skipped_count = 0

    db = SessionLocal()
    try:
        for name, description in DEFAULT_CATEGORIES:
            exists = db.query(Category).filter(Category.name == name).first()
            if exists:
                skipped_count += 1
                continue

            db.add(Category(name=name, description=description))
            created_count += 1

        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        print(f"默认分类初始化失败：请检查数据库连接和表结构。错误：{exc}")
        raise SystemExit(1) from exc
    finally:
        db.close()

    print(f"默认分类初始化完成，新增 {created_count} 个分类，跳过 {skipped_count} 个已存在分类")


if __name__ == "__main__":
    main()
