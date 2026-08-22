from sqlalchemy.orm import Session

from ..exceptions import ApiError
from ..repository.course import (
    check_name_exists,
    create_and_populate_course,
    retrieve_all,
    retrieve_by_id,
    retrieve_course_detail,
    retrieve_course_details_for_instructor,
    retrieve_course_details_for_student,
    soft_delete,
)
from ..repository.course import (
    update_course as update_course_repo,
)
from ..schemas.course import CourseCreate, CourseUpdate


def create_course(db: Session, data: CourseCreate, user_id: int) -> int:
    if check_name_exists(db, data.name):
        raise ApiError(
            409, "COURSE_NAME_ALREADY_EXISTS", "A course with this name already exists."
        )
    course = create_and_populate_course(db, data, user_id)
    return course.id


def update_course(
    db: Session, course_id: int, data: CourseUpdate, user_id: int
) -> None:
    course = retrieve_by_id(db, course_id)
    if not course:
        raise ApiError(404, "COURSE_NOT_FOUND", "Course not found.")
    if check_name_exists(db, data.name, exclude_id=course_id):
        raise ApiError(
            409, "COURSE_NAME_ALREADY_EXISTS", "A course with this name already exists."
        )
    update_course_repo(db, course, data, user_id)


def get_courses_for_instructor(db: Session, user_id: int) -> list[dict]:
    return retrieve_course_details_for_instructor(db, user_id)


def get_courses_for_student(db: Session, group_id: int) -> list[dict]:
    return retrieve_course_details_for_student(db, group_id)


def get_all_courses(db: Session) -> list[dict]:
    return [retrieve_course_detail(db, course.id) for course in retrieve_all(db)]


def get_course_by_id(db: Session, course_id: int) -> dict | None:
    return retrieve_course_detail(db, course_id)


def is_course_name_available(
    db: Session, name: str, exclude_id: int | None = None
) -> bool:
    return not check_name_exists(db, name, exclude_id)


def delete_course(db: Session, course_id: int) -> None:
    course = retrieve_by_id(db, course_id)
    if not course:
        raise ApiError(404, "COURSE_NOT_FOUND", "Course not found.")
    soft_delete(db, course)
