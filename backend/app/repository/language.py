from sqlalchemy.orm import Session

from ..models.language import Language


def retrieve_all(db: Session) -> list[Language]:
    return db.query(Language).filter(Language.is_active.is_(True)).all()


def retrieve_by_id(db: Session, language_id: int) -> Language | None:
    return (
        db.query(Language)
        .filter(Language.id == language_id, Language.is_active.is_(True))
        .first()
    )


def soft_delete(db: Session, language: Language) -> None:
    language.is_active = False
    db.commit()
