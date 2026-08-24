from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from ..exceptions import ApiError
from ..models.assignment import Assignment
from ..models.assignment_rule_group import AssignmentRuleGroup
from ..models.course import Course
from ..models.course_group import CourseGroup
from ..models.course_instructor import CourseInstructor
from ..models.course_submission_language import CourseSubmissionLanguage
from ..models.group import Group
from ..models.language import Language
from ..models.rule import Rule
from ..models.rule_group import RuleGroup
from ..models.submission_mode import SubmissionMode
from ..models.user import User
from ..repository.rule_group import retrieve_by_ids as retrieve_rule_groups_by_ids
from ..schemas.course import CourseCreate, CourseUpdate


def _validate_rule_group_links(db: Session, assignments: list) -> None:
    referenced_ids = {
        link.id for assignment in assignments for link in assignment.rule_groups
    }
    if not referenced_ids:
        return
    existing = {rg.id for rg in retrieve_rule_groups_by_ids(db, list(referenced_ids))}
    missing = referenced_ids - existing
    if missing:
        raise ApiError(
            400,
            "VALIDATION_ERROR",
            f"Rule group(s) not found: {', '.join(str(i) for i in sorted(missing))}.",
        )


def _validate_language_ids(
    db: Session, feedback_language_id: int, submission_language_ids: list
) -> None:
    referenced_ids = {feedback_language_id, *submission_language_ids}
    existing = {
        lang.id
        for lang in db.query(Language)
        .filter(Language.id.in_(referenced_ids), Language.is_active.is_(True))
        .all()
    }
    missing = referenced_ids - existing
    if missing:
        raise ApiError(
            400,
            "VALIDATION_ERROR",
            f"Language(s) not found: {', '.join(str(i) for i in sorted(missing))}.",
        )


def create_and_populate_course(db: Session, data: CourseCreate, user_id: int) -> Course:
    _validate_rule_group_links(db, data.assignments)
    _validate_language_ids(db, data.feedback_language_id, data.submission_language_ids)

    default_percentage = 100.0 / len(data.assignments) if data.assignments else None

    course = Course(
        name=data.name,
        start_date=data.start_date,
        end_date=data.end_date,
        max_amount_of_points=data.max_amount_of_points,
        feedback_language_id=data.feedback_language_id,
        created_by=user_id,
        updated_by=user_id,
    )
    db.add(course)
    db.flush()

    for lang_id in data.submission_language_ids:
        db.add(CourseSubmissionLanguage(course_id=course.id, language_id=lang_id))

    for instructor_id in data.instructor_ids:
        db.add(CourseInstructor(course_id=course.id, instructor_id=instructor_id))

    for assignment_data in data.assignments:
        percentage = (
            assignment_data.percentage_of_points_in_course or default_percentage
        )
        assignment = Assignment(
            name=assignment_data.name,
            start_date=assignment_data.start_date,
            end_date=assignment_data.end_date,
            submission_mode_id=assignment_data.submission_mode_id,
            percentage_of_points_in_course=percentage,
            course_id=course.id,
        )
        db.add(assignment)
        db.flush()

        for link in assignment_data.rule_groups:
            db.add(
                AssignmentRuleGroup(
                    assignment_id=assignment.id,
                    rule_group_id=link.id,
                    percentage_of_points_in_assignment=link.percentage_of_points_in_assignment,
                )
            )

    db.commit()
    db.refresh(course)
    return course


def retrieve_by_id(db: Session, course_id: int) -> Course:
    return (
        db.query(Course)
        .filter(Course.id == course_id, Course.is_active.is_(True))
        .first()
    )


def retrieve_all(db: Session) -> list[Course]:
    return db.query(Course).filter(Course.is_active.is_(True)).all()


def check_name_exists(db: Session, name: str, exclude_id: int | None = None) -> bool:
    query = db.query(Course).filter(
        func.lower(Course.name) == name.lower(), Course.is_active.is_(True)
    )
    if exclude_id is not None:
        query = query.filter(Course.id != exclude_id)
    return db.query(query.exists()).scalar()


def soft_delete(db: Session, course: Course) -> None:
    course.is_active = False
    db.commit()


def update_course(
    db: Session, course: Course, data: CourseUpdate, user_id: int
) -> Course:
    _validate_rule_group_links(db, data.assignments)
    _validate_language_ids(db, data.feedback_language_id, data.submission_language_ids)

    course.name = data.name
    course.start_date = data.start_date
    course.end_date = data.end_date
    course.max_amount_of_points = data.max_amount_of_points
    course.feedback_language_id = data.feedback_language_id
    course.updated_by = user_id
    course.updated_at = func.now()

    db.query(CourseSubmissionLanguage).filter(
        CourseSubmissionLanguage.course_id == course.id
    ).delete()
    for lang_id in data.submission_language_ids:
        db.add(CourseSubmissionLanguage(course_id=course.id, language_id=lang_id))

    db.query(CourseInstructor).filter(CourseInstructor.course_id == course.id).delete()
    for instructor_id in data.instructor_ids:
        db.add(CourseInstructor(course_id=course.id, instructor_id=instructor_id))

    existing_assignments = (
        db.query(Assignment).filter(Assignment.course_id == course.id).all()
    )
    existing_assignment_map = {a.id: a for a in existing_assignments}
    incoming_assignment_ids = {a.id for a in data.assignments if a.id is not None}

    default_percentage = 100.0 / len(data.assignments) if data.assignments else None

    for assignment in existing_assignments:
        if assignment.id not in incoming_assignment_ids:
            _delete_assignment(db, assignment)

    for assignment_data in data.assignments:
        percentage = (
            assignment_data.percentage_of_points_in_course or default_percentage
        )

        if assignment_data.id and assignment_data.id in existing_assignment_map:
            assignment = existing_assignment_map[assignment_data.id]
            assignment.name = assignment_data.name
            assignment.start_date = assignment_data.start_date
            assignment.end_date = assignment_data.end_date
            assignment.submission_mode_id = assignment_data.submission_mode_id
            assignment.percentage_of_points_in_course = percentage
        else:
            assignment = Assignment(
                name=assignment_data.name,
                start_date=assignment_data.start_date,
                end_date=assignment_data.end_date,
                submission_mode_id=assignment_data.submission_mode_id,
                percentage_of_points_in_course=percentage,
                course_id=course.id,
            )
            db.add(assignment)
            db.flush()

        _sync_rule_group_links(db, assignment, assignment_data.rule_groups)

    db.commit()
    db.refresh(course)
    return course


def _delete_assignment(db: Session, assignment: Assignment) -> None:
    """Delete an assignment and its rule group links (rule groups themselves are
    reusable and are not owned by the assignment, so they are left intact)."""
    db.query(AssignmentRuleGroup).filter(
        AssignmentRuleGroup.assignment_id == assignment.id
    ).delete()
    db.delete(assignment)


def _sync_rule_group_links(db: Session, assignment: Assignment, links: list) -> None:
    existing_args = {
        arg.rule_group_id: arg
        for arg in db.query(AssignmentRuleGroup)
        .filter(AssignmentRuleGroup.assignment_id == assignment.id)
        .all()
    }
    incoming_ids = {link.id for link in links}

    for rule_group_id, arg in existing_args.items():
        if rule_group_id not in incoming_ids:
            db.delete(arg)

    for link in links:
        if link.id in existing_args:
            existing_args[
                link.id
            ].percentage_of_points_in_assignment = (
                link.percentage_of_points_in_assignment
            )
        else:
            db.add(
                AssignmentRuleGroup(
                    assignment_id=assignment.id,
                    rule_group_id=link.id,
                    percentage_of_points_in_assignment=link.percentage_of_points_in_assignment,
                )
            )


def retrieve_course_details_for_instructor(db: Session, user_id: int) -> list[dict]:
    courses = retrieve_courses_for_instructor(db, user_id)
    return [retrieve_course_detail(db, c.id) for c in courses]


def retrieve_course_details_for_student(db: Session, group_id: int) -> list[dict]:
    courses = retrieve_courses_for_student(db, group_id)
    return [retrieve_course_detail(db, c.id) for c in courses]


def retrieve_courses_for_instructor(db: Session, user_id: int) -> list[Course]:
    return (
        db.query(Course)
        .outerjoin(CourseInstructor, CourseInstructor.course_id == Course.id)
        .filter(
            Course.is_active.is_(True),
            or_(
                Course.created_by == user_id,
                CourseInstructor.instructor_id == user_id,
            ),
        )
        .distinct()
        .all()
    )


def retrieve_courses_for_student(db: Session, group_id: int) -> list[Course]:
    return (
        db.query(Course)
        .join(CourseGroup, CourseGroup.course_id == Course.id)
        .filter(CourseGroup.group_id == group_id, Course.is_active.is_(True))
        .all()
    )


def retrieve_course_detail(db: Session, course_id: int) -> dict | None:
    course = (
        db.query(Course)
        .filter(Course.id == course_id, Course.is_active.is_(True))
        .first()
    )
    if not course:
        return None

    feedback_language = (
        db.query(Language).filter(Language.id == course.feedback_language_id).first()
    )

    submission_languages = (
        db.query(Language)
        .join(
            CourseSubmissionLanguage,
            CourseSubmissionLanguage.language_id == Language.id,
        )
        .filter(CourseSubmissionLanguage.course_id == course_id)
        .all()
    )

    student_groups = (
        db.query(Group)
        .join(CourseGroup, CourseGroup.group_id == Group.id)
        .filter(CourseGroup.course_id == course_id)
        .all()
    )

    instructors = (
        db.query(User)
        .join(CourseInstructor, CourseInstructor.instructor_id == User.id)
        .filter(CourseInstructor.course_id == course_id)
        .all()
    )

    created_by_user = (
        db.query(User).filter(User.id == course.created_by).first()
        if course.created_by
        else None
    )
    updated_by_user = (
        db.query(User).filter(User.id == course.updated_by).first()
        if course.updated_by
        else None
    )

    assignments = db.query(Assignment).filter(Assignment.course_id == course_id).all()

    assignment_details = []
    for assignment in assignments:
        submission_mode = (
            db.query(SubmissionMode)
            .filter(SubmissionMode.id == assignment.submission_mode_id)
            .first()
        )

        arg_rows = (
            db.query(AssignmentRuleGroup)
            .filter(AssignmentRuleGroup.assignment_id == assignment.id)
            .all()
        )

        rule_groups = []
        for arg in arg_rows:
            rg = db.query(RuleGroup).filter(RuleGroup.id == arg.rule_group_id).first()
            if not rg:
                continue
            rules = db.query(Rule).filter(Rule.rule_group_id == rg.id).all()
            rule_groups.append(
                {
                    "id": rg.id,
                    "name": rg.name,
                    "percentage_of_points_in_assignment": arg.percentage_of_points_in_assignment,
                    "rules": [
                        {
                            "id": r.id,
                            "name": r.name,
                            "user_description": r.user_description,
                            "include_in_prompt": r.include_in_prompt,
                        }
                        for r in rules
                    ],
                }
            )

        assignment_details.append(
            {
                "id": assignment.id,
                "name": assignment.name,
                "start_date": assignment.start_date,
                "end_date": assignment.end_date,
                "submission_mode_id": assignment.submission_mode_id,
                "submission_mode_name": submission_mode.name if submission_mode else "",
                "percentage_of_points_in_course": assignment.percentage_of_points_in_course,
                "rule_groups": rule_groups,
            }
        )

    return {
        "id": course.id,
        "name": course.name,
        "start_date": course.start_date,
        "end_date": course.end_date,
        "max_amount_of_points": course.max_amount_of_points,
        "feedback_language": {
            "id": feedback_language.id,
            "name": feedback_language.name,
            "short_name": feedback_language.short_name,
        }
        if feedback_language
        else None,
        "submission_languages": [
            {"id": l.id, "name": l.name, "short_name": l.short_name}
            for l in submission_languages
        ],
        "student_groups": [
            {"id": g.id, "name": g.name, "short_name": g.short_name}
            for g in student_groups
        ],
        "instructors": [
            {"id": u.id, "name": u.name, "surname": u.surname} for u in instructors
        ],
        "assignments": assignment_details,
        "audit": {
            "created_at": course.created_at,
            "created_by": {
                "id": created_by_user.id,
                "name": created_by_user.name,
                "surname": created_by_user.surname,
            }
            if created_by_user
            else None,
            "updated_at": course.updated_at,
            "updated_by": {
                "id": updated_by_user.id,
                "name": updated_by_user.name,
                "surname": updated_by_user.surname,
            }
            if updated_by_user
            else None,
        },
    }
