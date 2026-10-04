from sqlalchemy import and_, case
from sqlalchemy.orm import Session, aliased, defer

from ..models.assignment import Assignment
from ..models.course_student_instructor import CourseStudentInstructor
from ..models.feedback import Feedback
from ..models.fulfillment import Fulfillment
from ..models.rule import Rule
from ..models.rule_feedback_submission import RuleFeedbackSubmission
from ..models.rule_group import RuleGroup
from ..models.submission import Submission, SubmissionStatus
from ..models.user import User
from ..schemas.submission import RuleFeedbackSchema

UNICODE_COLLATION = "und-x-icu"


def retrieve_by_id(db: Session, id: int):
    return db.query(Submission).filter(Submission.id == id).first()


def retrieve_by_user_and_chapter(db: Session, user_id: int, chapter_id: int):
    return (
        db.query(Submission)
        .filter(Submission.user_id == user_id, Submission.chapter_id == chapter_id)
        .all()
    )


def retrieve_submission_in_course(db: Session, submission_id: int, course_id: int):
    return (
        db.query(
            Submission,
            Assignment,
            Submission.file_bytes.isnot(None).label("has_file"),
        )
        .options(defer(Submission.file_bytes), defer(Submission.text))
        .join(Assignment, Assignment.id == Submission.assignment_id)
        .filter(Submission.id == submission_id, Assignment.course_id == course_id)
        .first()
    )


def retrieve_rule_evaluations(db: Session, submission_id: int):
    return (
        db.query(
            Rule.id.label("rule_id"),
            Rule.name.label("rule_name"),
            Rule.user_description.label("rule_description"),
            Rule.rule_group_id,
            RuleGroup.name.label("rule_group_name"),
            Feedback.id.label("feedback_id"),
            Feedback.feedback_text,
            Feedback.final_feedback_text,
            Fulfillment.id.label("fulfillment_id"),
            Fulfillment.initial_fulfillment_value,
            Fulfillment.final_fulfillment_value,
        )
        .select_from(Fulfillment)
        .join(Feedback, Feedback.id == Fulfillment.feedback_id)
        .join(Rule, Rule.id == Feedback.rule_id)
        .outerjoin(RuleGroup, RuleGroup.id == Rule.rule_group_id)
        .filter(Fulfillment.submission_id == submission_id)
        .order_by(
            RuleGroup.name.collate(UNICODE_COLLATION).nulls_last(),
            RuleGroup.id,
            Rule.name.collate(UNICODE_COLLATION),
            Rule.id,
            Feedback.id,
        )
        .all()
    )


def update_final_rule_evaluation(
    db: Session,
    fulfillment_id: int,
    feedback_id: int,
    final_fulfillment_value: int,
    final_feedback_text: str,
) -> None:
    db.query(Fulfillment).filter(Fulfillment.id == fulfillment_id).update(
        {Fulfillment.final_fulfillment_value: final_fulfillment_value},
        synchronize_session=False,
    )
    db.query(Feedback).filter(Feedback.id == feedback_id).update(
        {Feedback.final_feedback_text: final_feedback_text},
        synchronize_session=False,
    )


def retrieve_submission_file(db: Session, submission_id: int):
    return (
        db.query(
            Submission.file_bytes,
            Submission.file_name,
            Submission.user_id,
            Assignment.course_id,
            Assignment.name.label("assignment_name"),
            User.index.label("student_index"),
        )
        .join(Assignment, Assignment.id == Submission.assignment_id)
        .join(User, User.id == Submission.user_id)
        .filter(Submission.id == submission_id)
        .first()
    )


def retrieve_completed_evaluative_submissions(
    db: Session, course_id: int, student_ids: list[int], evaluative_mode_id: int
):
    if not student_ids:
        return []
    return (
        db.query(
            Submission.id.label("submission_id"),
            Submission.user_id,
            Submission.status,
            Submission.submitted_at,
            Submission.graded,
            Submission.achieved_points_percentage,
            Assignment.id.label("assignment_id"),
            Assignment.name.label("assignment_name"),
            Assignment.start_date.label("assignment_start_date"),
            Assignment.end_date.label("assignment_end_date"),
            Assignment.percentage_of_points_in_course,
        )
        .join(Assignment, Assignment.id == Submission.assignment_id)
        .filter(
            Assignment.course_id == course_id,
            Assignment.submission_mode_id == evaluative_mode_id,
            Submission.user_id.in_(student_ids),
            Submission.status == SubmissionStatus.COMPLETED.value,
        )
        .order_by(Assignment.start_date, Submission.submitted_at, Submission.id)
        .all()
    )


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
