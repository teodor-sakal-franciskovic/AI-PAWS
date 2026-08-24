from sqlalchemy.orm import Session

from ..exceptions import ApiError
from ..models.course import Course
from ..models.rule_group import RuleGroup
from ..repository.rule_group import (
    create_rule_group as create_rule_group_repo,
)
from ..repository.rule_group import (
    name_exists,
    retrieve_all,
    retrieve_all_for_instructor,
    retrieve_by_id,
    retrieve_courses_for_rule_group,
    retrieve_rules_for_rule_group,
    retrieve_user_by_id,
    soft_delete,
)
from ..repository.rule_group import (
    update_rule_group as update_rule_group_repo,
)
from ..schemas.rule_group import RuleGroupCreate, RuleGroupUpdate


def _audit(db: Session, entity) -> dict:
    return {
        "created_at": entity.created_at,
        "created_by": retrieve_user_by_id(db, entity.created_by),
        "updated_at": entity.updated_at,
        "updated_by": retrieve_user_by_id(db, entity.updated_by),
    }


def _course_summary(db: Session, course: Course) -> dict:
    return {
        "id": course.id,
        "name": course.name,
        "audit": _audit(db, course),
    }


def _rule_group_fields(db: Session, rule_group: RuleGroup) -> dict:
    courses = [
        _course_summary(db, course)
        for course in retrieve_courses_for_rule_group(db, rule_group.id)
    ]
    return {
        "id": rule_group.id,
        "name": rule_group.name,
        "number_of_courses": len(courses),
        "courses": courses,
        "rules": retrieve_rules_for_rule_group(db, rule_group.id),
        "audit": _audit(db, rule_group),
    }


def get_all_rule_groups(db: Session) -> list[dict]:
    return [_rule_group_fields(db, rule_group) for rule_group in retrieve_all(db)]


def get_rule_groups_for_instructor(db: Session, user_id: int) -> list[dict]:
    return [
        _rule_group_fields(db, rule_group)
        for rule_group in retrieve_all_for_instructor(db, user_id)
    ]


def get_rule_group_detail(db: Session, rule_group_id: int) -> dict | None:
    rule_group = retrieve_by_id(db, rule_group_id)
    if not rule_group:
        return None
    return _rule_group_fields(db, rule_group)


def is_name_available(db: Session, name: str, exclude_id: int | None = None) -> bool:
    return not name_exists(db, name, exclude_id)


def create_rule_group(db: Session, data: RuleGroupCreate, user_id: int) -> int:
    if name_exists(db, data.name):
        raise ApiError(
            409,
            "RULE_GROUP_NAME_ALREADY_EXISTS",
            "A rule group with this name already exists.",
        )
    rule_group = create_rule_group_repo(db, data.name, data.rules, user_id)
    return rule_group.id


def update_rule_group(
    db: Session, rule_group_id: int, data: RuleGroupUpdate, user_id: int
) -> list[int]:
    """Returns rule IDs needing prompt generation."""
    rule_group = retrieve_by_id(db, rule_group_id)
    if not rule_group:
        raise ApiError(404, "RULE_GROUP_NOT_FOUND", "Rule group not found.")
    if name_exists(db, data.name, exclude_id=rule_group_id):
        raise ApiError(
            409,
            "RULE_GROUP_NAME_ALREADY_EXISTS",
            "A rule group with this name already exists.",
        )
    return update_rule_group_repo(db, rule_group, data.name, data.rules, user_id)


def delete_rule_group(db: Session, rule_group_id: int) -> None:
    rule_group = retrieve_by_id(db, rule_group_id)
    if not rule_group:
        raise ApiError(404, "RULE_GROUP_NOT_FOUND", "Rule group not found.")
    soft_delete(db, rule_group)
