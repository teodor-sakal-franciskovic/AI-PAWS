from sqlalchemy.orm import Session

from ..models.rule import Rule
from ..models.feedback import Feedback


# DEPRECATED
def retrieve_rules_for_chapter(
    db: Session, chapter_name: str, include_in_prompt: bool = False
):
    pass


def retrieve_by_id(db: Session, id: int):
    return db.query(Rule).filter(Rule.id == id).first()


def retrieve_rule_by_feedback_id(db: Session, feedback_id: int) -> Rule:
    return (
        db.query(Rule)
        .join(Feedback, Feedback.rule_id == Rule.id)
        .filter(Feedback.id == feedback_id)
        .first()
    )


def retrieve_all(db: Session):
    return db.query(Rule).all()
