from sqlalchemy.orm import Session

from ..models.rule_group import RuleGroup
from ..repository.rule_group import (
    count_courses_for_rule_group,
    name_exists,
    retrieve_all,
    retrieve_by_id,
    retrieve_rules_for_rule_group,
    retrieve_taken_names,
    retrieve_user_by_id,
)


def _rule_group_base_fields(db: Session, rule_group: RuleGroup) -> dict:
    return {
        "id": rule_group.id,
        "name": rule_group.name,
        "percentage_of_points_in_assignment": rule_group.percentage_of_points_in_assignment,
        "number_of_courses": count_courses_for_rule_group(db, rule_group.id),
        "rules": retrieve_rules_for_rule_group(db, rule_group.id),
        "created_by": retrieve_user_by_id(db, rule_group.created_by),
        "updated_by": retrieve_user_by_id(db, rule_group.updated_by),
    }


def get_all_rule_groups(db: Session) -> list[dict]:
    rule_groups = retrieve_all(db)
    return [_rule_group_base_fields(db, rule_group) for rule_group in rule_groups]


def get_rule_group_detail(db: Session, rule_group_id: int) -> dict | None:
    rule_group = retrieve_by_id(db, rule_group_id)
    if not rule_group:
        return None
    return {
        **_rule_group_base_fields(db, rule_group),
        "taken_rule_group_names": retrieve_taken_names(db, exclude_id=rule_group.id),
    }


def check_rule_group_name(
    db: Session, name: str, exclude_id: int | None = None
) -> bool:
    return name_exists(db, name, exclude_id)
