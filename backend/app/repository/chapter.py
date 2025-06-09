from sqlalchemy.orm import Session

from ..models.chapter import Chapter


def retrieve_all(db: Session):
    return db.query(Chapter).all()
