from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from ..models.assignment import Assignment
from ..models.assignment_rule_group import AssignmentRuleGroup
from ..models.course import Course
from ..models.course_instructor import CourseInstructor
from ..models.rule import Rule
from ..models.rule_group import RuleGroup
from ..models.user import User


def retrieve_all(db: Session) -> list[RuleGroup]:
    return db.query(RuleGroup).filter(RuleGroup.is_active.is_(True)).all()


def retrieve_all_for_instructor(db: Session, user_id: int) -> list[RuleGroup]:
    """Rule groups created by the instructor, plus rule groups used in any
    course the instructor created or is added to (mirrors retrieve_courses_for_instructor)."""
    return (
        db.query(RuleGroup)
        .outerjoin(
            AssignmentRuleGroup, AssignmentRuleGroup.rule_group_id == RuleGroup.id
        )
        .outerjoin(Assignment, Assignment.id == AssignmentRuleGroup.assignment_id)
        .outerjoin(Course, Course.id == Assignment.course_id)
        .outerjoin(CourseInstructor, CourseInstructor.course_id == Course.id)
        .filter(
            RuleGroup.is_active.is_(True),
            or_(
                RuleGroup.created_by == user_id,
                Course.created_by == user_id,
                CourseInstructor.instructor_id == user_id,
            ),
        )
        .distinct()
        .all()
    )


def retrieve_by_id(db: Session, rule_group_id: int) -> RuleGroup | None:
    return (
        db.query(RuleGroup)
        .filter(RuleGroup.id == rule_group_id, RuleGroup.is_active.is_(True))
        .first()
    )


def retrieve_by_ids(db: Session, rule_group_ids: list[int]) -> list[RuleGroup]:
    if not rule_group_ids:
        return []
    return (
        db.query(RuleGroup)
        .filter(RuleGroup.id.in_(rule_group_ids), RuleGroup.is_active.is_(True))
        .all()
    )


def retrieve_rules_for_rule_group(db: Session, rule_group_id: int) -> list[Rule]:
    return db.query(Rule).filter(Rule.rule_group_id == rule_group_id).all()


def retrieve_courses_for_rule_group(db: Session, rule_group_id: int) -> list[Course]:
    return (
        db.query(Course)
        .join(Assignment, Assignment.course_id == Course.id)
        .join(AssignmentRuleGroup, AssignmentRuleGroup.assignment_id == Assignment.id)
        .filter(
            AssignmentRuleGroup.rule_group_id == rule_group_id,
            Course.is_active.is_(True),
        )
        .distinct()
        .all()
    )


def retrieve_user_by_id(db: Session, user_id: int | None) -> User | None:
    if not user_id:
        return None
    return db.query(User).filter(User.id == user_id).first()


def name_exists(db: Session, name: str, exclude_id: int | None = None) -> bool:
    query = db.query(RuleGroup).filter(
        func.lower(RuleGroup.name) == name.lower(), RuleGroup.is_active.is_(True)
    )
    if exclude_id is not None:
        query = query.filter(RuleGroup.id != exclude_id)
    return db.query(query.exists()).scalar()


def soft_delete(db: Session, rule_group: RuleGroup) -> None:
    rule_group.is_active = False
    db.commit()


def create_rule_group(
    db: Session, name: str, rules_data: list, user_id: int
) -> RuleGroup:
    rule_group = RuleGroup(name=name, created_by=user_id, updated_by=user_id)
    db.add(rule_group)
    db.flush()

    for rule_data in rules_data:
        db.add(
            Rule(
                name=rule_data.name,
                user_description=rule_data.user_description,
                include_in_prompt=rule_data.include_in_prompt,
                prompt_description=None,
                rule_group_id=rule_group.id,
            )
        )

    db.commit()
    db.refresh(rule_group)
    return rule_group


def update_rule_group(
    db: Session, rule_group: RuleGroup, name: str, rules_data: list, user_id: int
) -> list[int]:
    """Updates the rule group and syncs its rules. Returns rule IDs needing prompt generation."""
    rule_group.name = name
    rule_group.updated_by = user_id
    rule_group.updated_at = func.now()

    rules_needing_generation: list[int] = []

    existing_rules = db.query(Rule).filter(Rule.rule_group_id == rule_group.id).all()
    existing_rule_map = {r.id: r for r in existing_rules}
    incoming_rule_ids = {r.id for r in rules_data if r.id is not None}

    for rule in existing_rules:
        if rule.id not in incoming_rule_ids:
            db.delete(rule)

    for rule_data in rules_data:
        if rule_data.id and rule_data.id in existing_rule_map:
            rule = existing_rule_map[rule_data.id]
            description_changed = rule.user_description != rule_data.user_description
            rule.name = rule_data.name
            rule.user_description = rule_data.user_description
            rule.include_in_prompt = rule_data.include_in_prompt
            if description_changed:
                rule.prompt_description = None
                db.flush()
                rules_needing_generation.append(rule.id)
        else:
            rule = Rule(
                name=rule_data.name,
                user_description=rule_data.user_description,
                include_in_prompt=rule_data.include_in_prompt,
                prompt_description=None,
                rule_group_id=rule_group.id,
            )
            db.add(rule)
            db.flush()
            rules_needing_generation.append(rule.id)

    db.commit()
    db.refresh(rule_group)
    return rules_needing_generation


def retrieve_rules_needing_prompt(db: Session, rule_group_id: int) -> list[Rule]:
    return (
        db.query(Rule)
        .filter(
            Rule.rule_group_id == rule_group_id,
            Rule.include_in_prompt == True,  # noqa: E712
            Rule.prompt_description == None,  # noqa: E711
        )
        .all()
    )
