from sqlalchemy import func
from sqlalchemy.orm import Session
from ..models.chapter import Chapter
from ..models.chapter_grading_aspect import ChapterGradingAspect
from ..models.grading_aspect import GradingAspect
from ..models.rule import Rule


def get_prompt_rules_for_chapter(db: Session, chapter_name: str):
    results = (
        db.query(
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
        .filter(Rule.include_in_prompt.is_(True))
        .all()
    )
    return results
