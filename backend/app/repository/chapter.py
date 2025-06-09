from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models.chapter import Chapter


def retrieve_all(db: Session):
    return db.query(Chapter).all()


def retrieve_by_name(db: Session, name: str):
    return db.query(Chapter).filter(func.lower(Chapter.name) == name.lower()).first()
