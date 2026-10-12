from datetime import datetime, timezone

from sqlalchemy import and_, distinct, func
from sqlalchemy.orm import Session, aliased

from ..models.assignment import Assignment
from ..models.assignment_rule_group import AssignmentRuleGroup
from ..models.course_group import CourseGroup
from ..models.course_student_instructor import CourseStudentInstructor
from ..models.rule import Rule
from ..models.rule_group import RuleGroup
from ..models.submission import Submission, SubmissionStatus
from ..models.user import User
from .submission import UNICODE_COLLATION


def retrieve_course_assignments(db: Session, course_id: int) -> list[Assignment]:
    return (
        db.query(Assignment)
        .filter(Assignment.course_id == course_id)
        .order_by(Assignment.start_date, Assignment.id)
        .all()
    )


def retrieve_rule_group_summaries(db: Session, assignment_ids: list[int]):
    if not assignment_ids:
        return []
    rules_per_group = (
        db.query(Rule.rule_group_id, func.count(Rule.id).label("rules_count"))
        .group_by(Rule.rule_group_id)
        .subquery()
    )
    return (
        db.query(
            AssignmentRuleGroup.assignment_id,
            RuleGroup.id,
            RuleGroup.name,
            AssignmentRuleGroup.percentage_of_points_in_assignment,
            func.coalesce(rules_per_group.c.rules_count, 0).label("rules_count"),
        )
        .join(RuleGroup, RuleGroup.id == AssignmentRuleGroup.rule_group_id)
        .outerjoin(rules_per_group, rules_per_group.c.rule_group_id == RuleGroup.id)
        .filter(AssignmentRuleGroup.assignment_id.in_(assignment_ids))
        .order_by(
            AssignmentRuleGroup.assignment_id,
            RuleGroup.name.collate(UNICODE_COLLATION),
            RuleGroup.id,
        )
        .all()
    )


def retrieve_submitted_counts(db: Session, assignment_ids: list[int]) -> dict[int, int]:
    if not assignment_ids:
        return {}
    rows = (
        db.query(Submission.assignment_id, func.count(distinct(Submission.user_id)))
        .filter(
            Submission.assignment_id.in_(assignment_ids),
            Submission.status == SubmissionStatus.COMPLETED.value,
        )
        .group_by(Submission.assignment_id)
        .all()
    )
    return {assignment_id: count for assignment_id, count in rows}


def retrieve_latest_submission_files(db: Session, assignment_id: int, course_id: int):
    Student = aliased(User)
    Instructor = aliased(User)
    return (
        db.query(
            Submission.file_bytes,
            Student.id.label("student_id"),
            Student.index.label("student_index"),
            Student.name.label("student_name"),
            Student.surname.label("student_surname"),
            Instructor.id.label("instructor_id"),
            Instructor.name.label("instructor_name"),
            Instructor.surname.label("instructor_surname"),
        )
        .join(Student, Student.id == Submission.user_id)
        .outerjoin(
            CourseStudentInstructor,
            and_(
                CourseStudentInstructor.student_id == Student.id,
                CourseStudentInstructor.course_id == course_id,
            ),
        )
        .outerjoin(Instructor, Instructor.id == CourseStudentInstructor.instructor_id)
        .filter(
            Submission.assignment_id == assignment_id,
            Submission.file_bytes.isnot(None),
        )
        .distinct(Submission.user_id)
        .order_by(Submission.user_id, Submission.submitted_at.desc(), Submission.id.desc())
        .yield_per(20)
    )


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
