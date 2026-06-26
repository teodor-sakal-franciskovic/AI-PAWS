from sqlalchemy.orm import Session

from ..models.course import Course
from ..models.rule_group import RuleGroup
from ..models.rule import Rule
from ..models.assignment import Assignment
from ..models.course_group import CourseGroup
from ..models.course_submission_language import CourseSubmissionLanguage
from ..models.assignment_rule_group import AssignmentRuleGroup
from ..models.language import Language  # noqa: F401
from ..schemas.course import CourseCreate


def create_and_populate_course(db: Session, data: CourseCreate) -> Course:
    default_percentage = 100.0 / len(data.assignments) if data.assignments else None

    course = Course(
        name=data.name,
        start_date=data.start_date,
        end_date=data.end_date,
        max_amount_of_points=data.max_amount_of_points,
        feedback_language_id=data.feedback_language_id,
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
            chapter_id=assignment_data.chapter_id,
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
