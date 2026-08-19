from sqlalchemy.orm import Session

from ..models.language import Language


def retrieve_all(db: Session) -> list[Language]:
    return db.query(Language).all()
