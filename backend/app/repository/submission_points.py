from sqlalchemy.orm import Session

from ..models.assignment import Assignment
from ..models.submission import Submission, SubmissionStatus
from ..models.submission_points import SubmissionPoints


def retrieve_by_submission_id(db: Session, submission_id: int) -> SubmissionPoints | None:
    return db.get(SubmissionPoints, submission_id)


def retrieve_completed_points_for_student(
    db: Session, course_id: int, student_id: int, submission_mode_id: int
):
    return (
        db.query(
            Submission.assignment_id,
            Submission.graded,
            SubmissionPoints.max_points,
            SubmissionPoints.final_points,
        )
        .join(Assignment, Assignment.id == Submission.assignment_id)
        .outerjoin(SubmissionPoints, SubmissionPoints.submission_id == Submission.id)
        .filter(
            Assignment.course_id == course_id,
            Assignment.submission_mode_id == submission_mode_id,
            Submission.user_id == student_id,
            Submission.status == SubmissionStatus.COMPLETED.value,
        )
        .order_by(Submission.submitted_at, Submission.id)
        .all()
    )


def save_submission_points(
    db: Session,
    submission_id: int,
    max_points: float | None,
    ai_suggested_points: float | None,
    final_points: float | None,
) -> SubmissionPoints:
    row = db.get(SubmissionPoints, submission_id)
    if row is None:
        row = SubmissionPoints(submission_id=submission_id)
        db.add(row)
    row.max_points = max_points
    row.ai_suggested_points = ai_suggested_points
    row.final_points = final_points
    db.flush()
    return row
