from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models.user import User


def search_students(
    db: Session,
    role_id: int,
    email: str | None = None,
    name: str | None = None,
    surname: str | None = None,
    faculty: str | None = None,
    index: str | None = None,
    page: int = 1,
    page_size: int = 25,
) -> tuple[list[User], int]:
    query = db.query(User).filter(User.role_id == role_id)

    if email:
        query = query.filter(User.email.ilike(f"%{email}%"))
    if name:
        query = query.filter(User.name.ilike(f"%{name}%"))
    if surname:
        query = query.filter(User.surname.ilike(f"%{surname}%"))
    if faculty:
        query = query.filter(User.faculty.ilike(f"%{faculty}%"))
    if index:
        query = query.filter(User.index.ilike(f"%{index}%"))

    total = query.with_entities(func.count(User.id)).scalar() or 0

    items = (
        query.order_by(User.surname, User.name)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def retrieve_by_ids(db: Session, user_ids: list[int]) -> list[User]:
    if not user_ids:
        return []
    return db.query(User).filter(User.id.in_(user_ids)).all()
