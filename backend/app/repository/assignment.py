from datetime import datetime, timezone

from sqlalchemy import and_, distinct, func
from sqlalchemy.orm import Session, aliased

from ..models.assignment import Assignment
from ..models.assignment_rule_group import AssignmentRuleGroup
from ..models.course import Course
from ..models.course_student_instructor import CourseStudentInstructor
from ..models.group_student import GroupStudent
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
        .filter(
            AssignmentRuleGroup.assignment_id.in_(assignment_ids),
            RuleGroup.is_active.is_(True),
        )
        .order_by(
            AssignmentRuleGroup.assignment_id,
            RuleGroup.name.collate(UNICODE_COLLATION),
            RuleGroup.id,
        )
        .all()
    )


def retrieve_assignment_rules(db: Session, assignment_id: int):
    return (
        db.query(
            RuleGroup.id.label("rule_group_id"),
            RuleGroup.name.label("rule_group_name"),
            AssignmentRuleGroup.percentage_of_points_in_assignment,
            Rule.id.label("rule_id"),
            Rule.name.label("rule_name"),
            Rule.user_description,
            Rule.generated_description,
            Rule.include_in_prompt,
        )
        .join(AssignmentRuleGroup, AssignmentRuleGroup.rule_group_id == RuleGroup.id)
        .join(Rule, Rule.rule_group_id == RuleGroup.id)
        .filter(
            AssignmentRuleGroup.assignment_id == assignment_id,
            RuleGroup.is_active.is_(True),
        )
        .order_by(
            RuleGroup.name.collate(UNICODE_COLLATION),
            RuleGroup.id,
            Rule.name.collate(UNICODE_COLLATION),
            Rule.id,
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


def _assignments_with_latest_submission(db: Session, student_id: int):
    return (
        db.query(Assignment, Submission)
        .join(Course, Course.id == Assignment.course_id)
        .join(GroupStudent, GroupStudent.course_id == Assignment.course_id)
        .outerjoin(
            Submission,
            and_(
                Submission.assignment_id == Assignment.id,
                Submission.user_id == student_id,
            ),
        )
        .filter(GroupStudent.student_id == student_id, Course.is_active.is_(True))
        .distinct(Assignment.id)
        .order_by(Assignment.id, Submission.submitted_at.desc(), Submission.id.desc())
    )


def retrieve_active_assignments_with_submissions(db: Session, student_id: int):
    now = datetime.now(timezone.utc)
    return (
        _assignments_with_latest_submission(db, student_id)
        .filter(Assignment.start_date <= now, Assignment.end_date >= now)
        .all()
    )


def retrieve_past_assignments_with_submissions(db: Session, student_id: int):
    now = datetime.now(timezone.utc)
    return (
        _assignments_with_latest_submission(db, student_id)
        .filter(Assignment.end_date < now)
        .all()
    )


def retrieve_by_id(db: Session, id: int):
    return db.query(Assignment).filter(Assignment.id == id).first()


def retrieve_all(db: Session):
    return db.query(Assignment).all()
