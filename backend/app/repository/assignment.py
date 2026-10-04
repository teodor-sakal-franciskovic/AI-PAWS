from datetime import datetime, timezone

from sqlalchemy import and_
from sqlalchemy.orm import Session

from ..models.assignment import Assignment
from ..models.assignment_rule_group import AssignmentRuleGroup
from ..models.course_group import CourseGroup
from ..models.submission import Submission


def retrieve_rule_group_percentages(
    db: Session, assignment_id: int
) -> dict[int, float | None]:
    rows = (
        db.query(
            AssignmentRuleGroup.rule_group_id,
            AssignmentRuleGroup.percentage_of_points_in_assignment,
        )
        .filter(AssignmentRuleGroup.assignment_id == assignment_id)
        .all()
    )
    return {rule_group_id: percentage for rule_group_id, percentage in rows}


def retrieve_active_assignments_for_group(
    db: Session, group_ids: list[int], user_id: int
):
    if not group_ids:
        return []
    now = datetime.now(timezone.utc)

    return (
        db.query(Assignment, Submission)
        .join(CourseGroup, Assignment.id == CourseGroup.assignment_id)
        .outerjoin(
            Submission,
            and_(
                Submission.assignment_id == Assignment.id,
                Submission.user_id == user_id,
            ),
        )
        .filter(
            Assignment.start_date <= now,
            Assignment.end_date >= now,
            CourseGroup.group_id.in_(group_ids),
        )
        .distinct()
        .all()
    )


def retrieve_past_submissions_with_assignments_for_user(
    db: Session, group_ids: list[int], user_id: int
):
    if not group_ids:
        return []
    now = datetime.now(timezone.utc)

    return (
        db.query(Assignment, Submission)
        .join(CourseGroup, Assignment.id == CourseGroup.assignment_id)
        .outerjoin(
            Submission,
            and_(
                Submission.assignment_id == Assignment.id,
                Submission.user_id == user_id,
            ),
        )
        .filter(
            Assignment.end_date < now,
            CourseGroup.group_id.in_(group_ids),
        )
        .distinct()
        .all()
    )


def retrieve_by_id(db: Session, id: int):
    return db.query(Assignment).filter(Assignment.id == id).first()


def retrieve_all(db: Session):
    return db.query(Assignment).all()
