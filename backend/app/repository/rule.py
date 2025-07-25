from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models.chapter import Chapter
from ..models.chapter_grading_aspect import ChapterGradingAspect
from ..models.grading_aspect import GradingAspect
from ..models.rule import Rule
from ..models.feedback import Feedback


def retrieve_rules_for_chapter(
    db: Session, chapter_name: str, include_in_prompt: bool = False
):
    query = (
        db.query(
            Rule.id.label("rule_id"),
            Rule.name.label("rule_name"),
            Rule.description.label("rule_description"),
        )
        .join(GradingAspect, Rule.grading_aspect_id == GradingAspect.id)
        .join(
            ChapterGradingAspect,
            GradingAspect.id == ChapterGradingAspect.grading_aspect_id,
        )
        .join(Chapter, Chapter.id == ChapterGradingAspect.chapter_id)
        .filter(func.lower(Chapter.name) == chapter_name.lower())
    )

    if include_in_prompt:
        query = query.filter(Rule.include_in_prompt.is_(True))

    results = query.all()
    return results


def retrieve_by_id(db: Session, id: int):
    return db.query(Rule).filter(Rule.id == id).first()


def retrieve_rule_by_feedback_id(db: Session, feedback_id: int) -> Rule:
    return (
        db.query(Rule)
        .join(Feedback, Feedback.rule_id == Rule.id)
        .filter(Feedback.id == feedback_id)
        .first()
    )
