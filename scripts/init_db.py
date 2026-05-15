"""Initialize MySQL database tables.

Run this script from the project root after configuring .env and creating the
target MySQL database.
"""

from pathlib import Path
import sys


BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND_DIR))


def main() -> None:
    try:
        from sqlalchemy.exc import SQLAlchemyError

        from app.database import init_database
    except ModuleNotFoundError as exc:
        print(f"数据库初始化失败：缺少依赖 {exc.name}，请先安装 backend/requirements.txt")
        raise SystemExit(1) from exc

    try:
        init_database()
    except SQLAlchemyError as exc:
        print(f"数据库初始化失败：请检查 DATABASE_URL、MySQL 服务和目标数据库。错误：{exc}")
        raise SystemExit(1) from exc

    print("数据库表初始化完成")


if __name__ == "__main__":
    main()
