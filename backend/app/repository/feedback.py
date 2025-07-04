from sqlalchemy.orm import Session

from ..models.feedback import Feedback


def retrieve_by_id(db: Session, id: int):
    return db.query(Feedback).filter(Feedback.id == id).first()


def update_with_additional_text(db: Session, id: int, additional_text: str):
    feedback = retrieve_by_id(db, id)
    feedback.additional_text = additional_text
    db.commit()
    db.refresh(feedback)
    return feedback
