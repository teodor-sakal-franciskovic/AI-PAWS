from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models.assignment import Assignment
from ..models.assignment_rule_group import AssignmentRuleGroup
from ..models.rule import Rule
from ..models.rule_group import RuleGroup
from ..models.user import User


def retrieve_all(db: Session) -> list[RuleGroup]:
    return db.query(RuleGroup).all()


def retrieve_by_id(db: Session, rule_group_id: int) -> RuleGroup | None:
    return db.query(RuleGroup).filter(RuleGroup.id == rule_group_id).first()


def retrieve_rules_for_rule_group(db: Session, rule_group_id: int) -> list[Rule]:
    return db.query(Rule).filter(Rule.rule_group_id == rule_group_id).all()


def count_courses_for_rule_group(db: Session, rule_group_id: int) -> int:
    return (
        db.query(func.count(func.distinct(Assignment.course_id)))
        .join(AssignmentRuleGroup, AssignmentRuleGroup.assignment_id == Assignment.id)
        .filter(AssignmentRuleGroup.rule_group_id == rule_group_id)
        .scalar()
        or 0
    )


def retrieve_user_by_id(db: Session, user_id: int | None) -> User | None:
    if not user_id:
        return None
    return db.query(User).filter(User.id == user_id).first()


def retrieve_taken_names(db: Session, exclude_id: int | None = None) -> list[str]:
    query = db.query(RuleGroup.name)
    if exclude_id is not None:
        query = query.filter(RuleGroup.id != exclude_id)
    return [name for (name,) in query.all()]


def name_exists(db: Session, name: str, exclude_id: int | None = None) -> bool:
    query = db.query(RuleGroup).filter(func.lower(RuleGroup.name) == name.lower())
    if exclude_id is not None:
        query = query.filter(RuleGroup.id != exclude_id)
    return db.query(query.exists()).scalar()
