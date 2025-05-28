from sqlalchemy.orm import Session

from ..models.role import Role
from ..schemas.user import UserCreate


def retrieve_all(db: Session):
    return db.query(Role).all()


def retrieve_by_id(db: Session, user: UserCreate):
    return db.query(Role).filter(Role.id == user.role_id).first()


def retrieve_by_name(db: Session, name: str):
    return db.query(Role).filter(Role.name == name).first()