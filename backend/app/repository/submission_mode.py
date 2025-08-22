from sqlalchemy.orm import Session

from ..models.submission_mode import SubmissionMode


def retrieve_by_name(db: Session, name: str):
    return db.query(SubmissionMode).filter(SubmissionMode.name == name).first()


def retrieve_by_id(db: Session, id: int):
    return db.query(SubmissionMode).filter(SubmissionMode.id == id).first()


def retrieve_all(db: Session):
    return db.query(SubmissionMode).all()
