from sqlalchemy.orm import Session

from app.models import Category
from app.schemas.category import CategoryCreate


def list_categories(db: Session) -> list[Category]:
    return db.query(Category).order_by(Category.id.asc()).all()


def get_category_by_id(db: Session, category_id: int) -> Category | None:
    return db.query(Category).filter(Category.id == category_id).first()


def get_category_by_name(db: Session, name: str) -> Category | None:
    return db.query(Category).filter(Category.name == name).first()


def create_category(db: Session, data: CategoryCreate) -> Category:
    category = Category(
        name=data.name.strip(),
        description=data.description,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def detect_category_by_question(question: str, db: Session) -> Category | None:
    keyword_map = {
        "社会保障": ["社保", "养老", "失业", "工伤"],
        "医疗卫生": ["医保", "医疗", "医院", "报销"],
        "教育服务": ["学校", "入学", "教育", "学生"],
        "就业创业": ["就业", "创业", "补贴", "招聘"],
        "住房保障": ["住房", "公积金", "租房", "买房"],
        "交通出行": ["公交", "地铁", "驾驶证", "交通"],
        "城市管理": ["投诉", "占道", "噪声", "城管"],
    }

    for category_name, keywords in keyword_map.items():
        if any(keyword in question for keyword in keywords):
            return get_category_by_name(db, category_name)

    return get_category_by_name(db, "其他咨询")
