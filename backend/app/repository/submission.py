from sqlalchemy import and_, case
from sqlalchemy.orm import Session, aliased

from ..models.assignment import Assignment
from ..models.course_student_instructor import CourseStudentInstructor
from ..models.feedback import Feedback
from ..models.fulfillment import Fulfillment
from ..models.rule import Rule
from ..models.rule_feedback_submission import RuleFeedbackSubmission
from ..models.submission import Submission, SubmissionStatus
from ..models.user import User
from ..schemas.submission import RuleFeedbackSchema


def retrieve_by_id(db: Session, id: int):
    return db.query(Submission).filter(Submission.id == id).first()


def retrieve_by_user_and_chapter(db: Session, user_id: int, chapter_id: int):
    return (
        db.query(Submission)
        .filter(Submission.user_id == user_id, Submission.chapter_id == chapter_id)
        .all()
    )


def update_grade(db: Session, id: int, percentage: float):
    submission = db.query(Submission).filter(Submission.id == id).first()
    submission.achieved_points_percentage = percentage
    submission.graded = True
    db.commit()
    return submission


def update_status(db: Session, id: int, status: SubmissionStatus):
    submission = db.query(Submission).filter(Submission.id == id).first()
    submission.status = status
    db.commit()
    return submission


def retrieve_by_assignment_id(db: Session, assignment_id: int):
    Student = aliased(User)
    TA = aliased(User)

    return (
        db.query(Submission, Student, TA)
        .join(Student, Submission.user_id == Student.id)
        .join(Assignment, Assignment.id == Submission.assignment_id)
        .outerjoin(
            CourseStudentInstructor,
            and_(
                CourseStudentInstructor.student_id == Student.id,
                CourseStudentInstructor.course_id == Assignment.course_id,
            ),
        )
        .outerjoin(TA, CourseStudentInstructor.instructor_id == TA.id)
        .filter(Submission.assignment_id == assignment_id)
        .all()
    )


def retrieve_rule_feedbacks_for_submission(
    session: Session, submission_id: int
) -> list[RuleFeedbackSchema]:
    rows = (
        session.query(
            Feedback.id.label("feedback_id"),
            Feedback.is_valid,
            Feedback.initially_fulfilled,
            Rule.name.label("rule_name"),
            Rule.description.label("rule_description"),
            case(
                (
                    Feedback.final_feedback_text.isnot(None),
                    Feedback.final_feedback_text,
                ),
                else_=Feedback.feedback_text,
            ).label("feedback_text"),
            Feedback.additional_text.label("additional_feedback_text"),
            case(
                (
                    Fulfillment.final_fulfillment_value.isnot(None),
                    Fulfillment.final_fulfillment_value,
                ),
                else_=Fulfillment.initial_fulfillment_value,
            ).label("fulfillment_value"),
        )
        .join(Rule, Rule.id == Feedback.rule_id)
        .join(RuleFeedbackSubmission, RuleFeedbackSubmission.feedback_id == Feedback.id)
        .outerjoin(Fulfillment, Fulfillment.feedback_id == Feedback.id)
        .filter(RuleFeedbackSubmission.submission_id == submission_id)
        .all()
    )

    return [RuleFeedbackSchema(**row._asdict()) for row in rows]
