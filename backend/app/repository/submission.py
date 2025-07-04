from sqlalchemy.orm import Session

from ..models.submission import Submission


def retrieve_by_id(db: Session, id: int):
    return db.query(Submission).filter(Submission.id == id).first()
