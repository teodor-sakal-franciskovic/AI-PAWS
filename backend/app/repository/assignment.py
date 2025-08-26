from sqlalchemy.orm import Session

from datetime import datetime, timezone

from ..models.assignment import Assignment
from ..models.assignment_group import AssignmentGroup
from ..models.submission import Submission


def retrieve_active_assignments_for_group(db: Session, group_id: str):
    now = datetime.now(timezone.utc)

    return (
        db.query(Submission, Assignment)
        .join(AssignmentGroup, Assignment.id == AssignmentGroup.assignment_id)
        .join(Submission, Submission.assignment_id == Assignment.id)
        .filter(
            Assignment.start_date <= now,
            Assignment.end_date >= now,
            AssignmentGroup.group_id == group_id,
        )
        .all()
    )


def retrieve_past_submissions_with_assignments_for_user(db: Session, user_id: int):
    now = datetime.now(timezone.utc)

    return (
        db.query(Submission, Assignment)
        .join(Assignment, Submission.assignment_id == Assignment.id)
        .filter(
            Submission.user_id == user_id,
            Assignment.end_date < now,
        )
        .all()
    )


def retrieve_by_id(db: Session, id: int):
    return db.query(Assignment).filter(Assignment.id == id).first()


def retrieve_all(db: Session):
    return db.query(Assignment).all()
