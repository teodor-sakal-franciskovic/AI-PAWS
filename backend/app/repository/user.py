from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from ..schemas.user import UserCreate
from ..models.user import User
from ..models.submission import Submission
from ..models.rule_feedback_submission import RuleFeedbackSubmission
from ..models.rule import Rule
from ..models.feedback import Feedback
from ..models.fulfillment import Fulfillment


def retrieve_by_email_from_user(db: Session, user: UserCreate):
    return db.query(User).filter(User.email == user.email).first()


def retrieve_by_email(db: Session, username: str):
    return db.query(User).filter(User.email == username).first()


def retrieve_evaluative_submissions(
    session, ta_id: int, evaluative_submission_mode_id: int
):
    stmt = (
        select(
            User.id.label("user_id"),
            User.index.label("user_index"),
            User.name.label("user_name"),
            User.surname.label("user_surname"),
            Submission.id.label("submission_id"),
            Submission.submitted_at,
            Submission.gd_file_link,
            Submission.achieved_points_percentage,
            Rule.id.label("rule_id"),
            Rule.name.label("rule_name"),
            Rule.description.label("rule_description"),
            Feedback.id.label("feedback_id"),
            Feedback.feedback_text,
            Feedback.final_feedback_text,
            Fulfillment.id.label("fulfillment_id"),
            Fulfillment.initial_fulfillment_value,
            Fulfillment.final_fulfillment_value,
        )
        .select_from(User)
        .join(Submission, Submission.user_id == User.id)
        .join(
            RuleFeedbackSubmission,
            RuleFeedbackSubmission.submission_id == Submission.id,
        )
        .join(Rule, Rule.id == RuleFeedbackSubmission.rule_id)
        .join(Feedback, Feedback.id == RuleFeedbackSubmission.feedback_id)
        .outerjoin(
            Fulfillment,
            and_(
                Fulfillment.feedback_id == Feedback.id,
                Fulfillment.submission_id == Submission.id,
            ),
        )
        .where(
            User.is_active.is_(True),
            User.assigned_to_ta == ta_id,
            Submission.submission_mode_id == evaluative_submission_mode_id,
        )
        .order_by(User.id, Submission.id, Rule.id)
    )

    result = session.execute(stmt).fetchall()
    return result
