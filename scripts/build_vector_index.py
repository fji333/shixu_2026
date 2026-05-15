"""Build local Chroma vector index for active knowledge documents."""

from pathlib import Path
import sys


BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND_DIR))


def main() -> None:
    try:
        from sqlalchemy.exc import SQLAlchemyError

        from app.database import SessionLocal
        from app.services.vector_service import rebuild_vector_index
    except ModuleNotFoundError as exc:
        print(f"向量索引构建失败：缺少依赖 {exc.name}，请先安装 backend/requirements.txt")
        raise SystemExit(1) from exc

    db = SessionLocal()
    try:
        result = rebuild_vector_index(db)
    except RuntimeError as exc:
        print(f"向量索引构建失败：{exc}")
        raise SystemExit(1) from exc
    except SQLAlchemyError as exc:
        print(f"向量索引构建失败：请检查数据库连接和表结构。错误：{exc}")
        raise SystemExit(1) from exc
    finally:
        db.close()

    print("向量索引构建完成")
    print(f"处理文档数：{result.document_count}")
    print(f"生成 chunks 数：{result.chunk_count}")
    print(f"写入向量数：{result.vector_count}")
    print(f"Chroma 存储路径：{result.vector_db_path}")


if __name__ == "__main__":
    main()
