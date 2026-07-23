from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from ..models.course import Course
from ..models.rule_group import RuleGroup
from ..models.rule import Rule
from ..models.assignment import Assignment
from ..models.course_group import CourseGroup
from ..models.course_submission_language import CourseSubmissionLanguage
from ..models.assignment_rule_group import AssignmentRuleGroup
from ..models.language import Language  # noqa: F401
from ..models.group import Group
from ..models.submission_mode import SubmissionMode
from ..models.user import User
from ..models.course_instructor import CourseInstructor
from ..schemas.course import CourseUpdate
from ..schemas.course import CourseCreate


def create_and_populate_course(db: Session, data: CourseCreate, user_id: int) -> Course:
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

    for group_id in data.group_ids:
        db.add(CourseGroup(course_id=course.id, group_id=group_id))

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

        for rg_data in assignment_data.rule_groups:
            rule_group = RuleGroup(
                name=rg_data.name,
                percentage_of_points_in_assignment=rg_data.percentage_of_points_in_assignment,
            )
            db.add(rule_group)
            db.flush()

            db.add(
                AssignmentRuleGroup(
                    assignment_id=assignment.id,
                    rule_group_id=rule_group.id,
                )
            )

            for rule_data in rg_data.rules:
                db.add(
                    Rule(
                        name=rule_data.name,
                        user_description=rule_data.user_description,
                        include_in_prompt=rule_data.include_in_prompt,
                        prompt_description=None,
                        rule_group_id=rule_group.id,
                    )
                )

    db.commit()
    db.refresh(course)
    return course


def retrieve_by_id(db: Session, course_id: int) -> Course:
    return db.query(Course).filter(Course.id == course_id).first()


def retrieve_rules_for_course(db: Session, course_id: int) -> list[Rule]:
    return (
        db.query(Rule)
        .join(RuleGroup, Rule.rule_group_id == RuleGroup.id)
        .join(AssignmentRuleGroup, AssignmentRuleGroup.rule_group_id == RuleGroup.id)
        .join(Assignment, Assignment.id == AssignmentRuleGroup.assignment_id)
        .filter(
            Assignment.course_id == course_id,
            Rule.include_in_prompt == True,
            Rule.prompt_description == None,
        )
        .all()
    )


def update_course(
    db: Session, course: Course, data: CourseUpdate, user_id: int
) -> tuple[Course, list[int]]:
    """Returns (updated_course, rule_ids_needing_prompt_generation)."""
    rules_needing_generation: list[int] = []

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

    db.query(CourseGroup).filter(CourseGroup.course_id == course.id).delete()
    for group_id in data.group_ids:
        db.add(CourseGroup(course_id=course.id, group_id=group_id))

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
            _delete_assignment_tree(db, assignment)

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

        new_rule_ids = _sync_rule_groups(db, assignment, assignment_data.rule_groups)
        rules_needing_generation.extend(new_rule_ids)

    db.commit()
    db.refresh(course)
    return course, rules_needing_generation


def _delete_assignment_tree(db: Session, assignment: Assignment) -> None:
    """Delete an assignment and its rule groups/rules."""
    arg_rows = (
        db.query(AssignmentRuleGroup)
        .filter(AssignmentRuleGroup.assignment_id == assignment.id)
        .all()
    )
    for arg in arg_rows:
        db.query(Rule).filter(Rule.rule_group_id == arg.rule_group_id).delete()
        db.query(RuleGroup).filter(RuleGroup.id == arg.rule_group_id).delete()
    db.query(AssignmentRuleGroup).filter(
        AssignmentRuleGroup.assignment_id == assignment.id
    ).delete()
    db.delete(assignment)


def _sync_rule_groups(
    db: Session, assignment: Assignment, rule_groups_data: list
) -> list[int]:
    """Sync rule groups for an assignment. Returns rule IDs needing prompt generation."""
    rules_needing_generation: list[int] = []

    existing_args = (
        db.query(AssignmentRuleGroup)
        .filter(AssignmentRuleGroup.assignment_id == assignment.id)
        .all()
    )
    existing_rg_ids = {arg.rule_group_id for arg in existing_args}
    existing_rg_map = {
        rg.id: rg
        for rg in db.query(RuleGroup).filter(RuleGroup.id.in_(existing_rg_ids)).all()
    }
    incoming_rg_ids = {rg.id for rg in rule_groups_data if rg.id is not None}

    for rg_id in existing_rg_ids:
        if rg_id not in incoming_rg_ids:
            db.query(Rule).filter(Rule.rule_group_id == rg_id).delete()
            db.query(AssignmentRuleGroup).filter(
                AssignmentRuleGroup.rule_group_id == rg_id
            ).delete()
            db.query(RuleGroup).filter(RuleGroup.id == rg_id).delete()

    for rg_data in rule_groups_data:
        if rg_data.id and rg_data.id in existing_rg_map:
            rule_group = existing_rg_map[rg_data.id]
            rule_group.name = rg_data.name
            rule_group.percentage_of_points_in_assignment = (
                rg_data.percentage_of_points_in_assignment
            )
        else:
            rule_group = RuleGroup(
                name=rg_data.name,
                percentage_of_points_in_assignment=rg_data.percentage_of_points_in_assignment,
            )
            db.add(rule_group)
            db.flush()
            db.add(
                AssignmentRuleGroup(
                    assignment_id=assignment.id,
                    rule_group_id=rule_group.id,
                )
            )

        new_rule_ids = _sync_rules(db, rule_group, rg_data.rules)
        rules_needing_generation.extend(new_rule_ids)

    return rules_needing_generation


def _sync_rules(db: Session, rule_group: RuleGroup, rules_data: list) -> list[int]:
    """Sync rules for a rule group. Returns IDs of rules needing prompt generation."""
    rules_needing_generation: list[int] = []

    existing_rules = db.query(Rule).filter(Rule.rule_group_id == rule_group.id).all()
    existing_rule_map = {r.id: r for r in existing_rules}
    incoming_rule_ids = {r.id for r in rules_data if r.id is not None}

    for rule in existing_rules:
        if rule.id not in incoming_rule_ids:
            db.delete(rule)

    for rule_data in rules_data:
        if rule_data.id and rule_data.id in existing_rule_map:
            rule = existing_rule_map[rule_data.id]
            description_changed = rule.user_description != rule_data.user_description
            rule.name = rule_data.name
            rule.user_description = rule_data.user_description
            rule.include_in_prompt = rule_data.include_in_prompt
            if description_changed:
                rule.prompt_description = None
                db.flush()
                rules_needing_generation.append(rule.id)
        else:
            rule = Rule(
                name=rule_data.name,
                user_description=rule_data.user_description,
                include_in_prompt=rule_data.include_in_prompt,
                prompt_description=None,
                rule_group_id=rule_group.id,
            )
            db.add(rule)
            db.flush()
            rules_needing_generation.append(rule.id)

    return rules_needing_generation


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
            or_(
                Course.created_by == user_id,
                CourseInstructor.instructor_id == user_id,
            )
        )
        .distinct()
        .all()
    )


def retrieve_courses_for_student(db: Session, group_id: int) -> list[Course]:
    return (
        db.query(Course)
        .join(CourseGroup, CourseGroup.course_id == Course.id)
        .filter(CourseGroup.group_id == group_id)
        .all()
    )


def retrieve_course_detail(db: Session, course_id: int) -> dict | None:
    course = db.query(Course).filter(Course.id == course_id).first()
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

    groups = (
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
        rg_ids = [arg.rule_group_id for arg in arg_rows]

        rule_groups = []
        for rg_id in rg_ids:
            rg = db.query(RuleGroup).filter(RuleGroup.id == rg_id).first()
            rules = db.query(Rule).filter(Rule.rule_group_id == rg_id).all()
            rule_groups.append(
                {
                    "id": rg.id,
                    "name": rg.name,
                    "percentage_of_points_in_assignment": rg.percentage_of_points_in_assignment,
                    "rules": [
                        {
                            "id": r.id,
                            "name": r.name,
                            "user_description": r.user_description,
                            "prompt_description": r.prompt_description,
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
        "groups": [{"id": g.id, "name": g.name} for g in groups],
        "created_by": {
            "id": created_by_user.id,
            "name": created_by_user.name,
            "surname": created_by_user.surname,
        }
        if created_by_user
        else None,
        "updated_by": {
            "id": updated_by_user.id,
            "name": updated_by_user.name,
            "surname": updated_by_user.surname,
        }
        if updated_by_user
        else None,
        "instructors": [
            {"id": u.id, "name": u.name, "surname": u.surname} for u in instructors
        ],
        "assignments": assignment_details,
    }
