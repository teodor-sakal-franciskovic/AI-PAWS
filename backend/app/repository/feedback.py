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


def update_final_feedback_text(db: Session, id: int, new_comment: str):
    feedback = retrieve_by_id(db, id)
    feedback.final_feedback_text = new_comment
    db.commit()
    db.refresh(feedback)
    return feedback


def update_is_valid(db: Session, id: int, is_valid: bool):
    feedback = retrieve_by_id(db, id)
    feedback.is_valid = is_valid
    db.commit()
    db.refresh(feedback)
    return feedback
