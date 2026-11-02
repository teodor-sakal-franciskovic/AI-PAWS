from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from ..models.assignment_rule_group import AssignmentRuleGroup
from ..models.rule import Rule
from ..models.rule_group import RuleGroup


# DEPRECATED
def retrieve_rules_for_chapter(
    db: Session, chapter_name: str, include_in_prompt: bool = False
):
    pass


def retrieve_rules_for_assignment(db: Session, assignment_id: int):
    return (
        db.query(
            Rule.id.label("rule_id"),
            Rule.name.label("rule_name"),
            func.coalesce(Rule.prompt_description, Rule.user_description).label(
                "rule_description"
            ),
            Rule.user_description,
            Rule.include_in_prompt,
            Rule.rule_group_id,
            or_(
                Rule.prompt_description.is_(None), Rule.generated_description.is_(None)
            ).label("needs_compiling"),
        )
        .join(
            AssignmentRuleGroup,
            AssignmentRuleGroup.rule_group_id == Rule.rule_group_id,
        )
        .join(RuleGroup, RuleGroup.id == Rule.rule_group_id)
        .filter(
            AssignmentRuleGroup.assignment_id == assignment_id,
            RuleGroup.is_active.is_(True),
        )
        .order_by(Rule.rule_group_id, Rule.id)
        .all()
    )


def retrieve_by_id(db: Session, id: int):
    return db.query(Rule).filter(Rule.id == id).first()


def retrieve_all(db: Session):
    return db.query(Rule).all()
