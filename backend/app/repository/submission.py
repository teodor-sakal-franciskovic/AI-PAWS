from sqlalchemy.orm import Session

from ..models.submission import Submission


def retrieve_by_id(db: Session, id: int):
    return db.query(Submission).filter(Submission.id == id).first()


def retrieve_by_user_and_chapter(db: Session, user_id: int, chapter_id: int):
    return (
        db.query(Submission)
        .filter(Submission.user_id == user_id, Submission.chapter_id == chapter_id)
        .all()
    )
