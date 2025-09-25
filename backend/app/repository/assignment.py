from sqlalchemy.orm import Session
from sqlalchemy import and_

from datetime import datetime, timezone

from ..models.assignment import Assignment
from ..models.assignment_group import AssignmentGroup
from ..models.submission import Submission


def retrieve_active_assignments_for_group(db: Session, group_id: int, user_id: int):
    now = datetime.now(timezone.utc)

    return (
        db.query(Assignment, Submission)
        .join(AssignmentGroup, Assignment.id == AssignmentGroup.assignment_id)
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
            AssignmentGroup.group_id == group_id,
        )
        .all()
    )


def retrieve_past_submissions_with_assignments_for_user(
    db: Session, group_id: int, user_id: int
):
    now = datetime.now(timezone.utc)

    return (
        db.query(Assignment, Submission)
        .join(AssignmentGroup, Assignment.id == AssignmentGroup.assignment_id)
        .outerjoin(
            Submission,
            and_(
                Submission.assignment_id == Assignment.id,
                Submission.user_id == user_id,
            ),
        )
        .filter(
            Assignment.end_date < now,
            AssignmentGroup.group_id == group_id,
        )
        .all()
    )


def retrieve_by_id(db: Session, id: int):
    return db.query(Assignment).filter(Assignment.id == id).first()


def retrieve_all(db: Session):
    return db.query(Assignment).all()
