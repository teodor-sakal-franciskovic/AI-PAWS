from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..models.course import Course
from ..repository.course import (
    check_name_exists,
    create_and_populate_course,
    retrieve_all,
    retrieve_by_id,
    retrieve_course_detail,
    retrieve_course_details_for_instructor,
    retrieve_course_details_for_student,
    retrieve_taken_names,
)
from ..repository.course import (
    update_course as update_course_repo,
)
from ..schemas.course import CourseCreate, CourseUpdate


def create_course(db: Session, data: CourseCreate, user_id: int) -> Course:
    return create_and_populate_course(db, data, user_id)


def update_course(
    db: Session, course_id: int, data: CourseUpdate, user_id: int
) -> tuple[Course, list[int]]:
    course = retrieve_by_id(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return update_course_repo(db, course, data, user_id)


def get_courses_for_instructor(db: Session, user_id: int) -> list[dict]:
    return retrieve_course_details_for_instructor(db, user_id)


def get_courses_for_student(db: Session, group_id: int) -> list[dict]:
    return retrieve_course_details_for_student(db, group_id)


def get_all_courses(db: Session) -> list[dict]:
    return [retrieve_course_detail(db, course.id) for course in retrieve_all(db)]


def get_course_by_id(db: Session, course_id: int) -> dict | None:
    detail = retrieve_course_detail(db, course_id)
    if not detail:
        return None
    detail["taken_course_names"] = retrieve_taken_names(db, exclude_id=course_id)
    return detail


def check_course_name(db: Session, name: str, exclude_id: int | None = None) -> bool:
    return check_name_exists(db, name, exclude_id)
