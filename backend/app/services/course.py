from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..repository.course import (
    create_and_populate_course,
    retrieve_by_id,
    retrieve_course_details_for_student,
    retrieve_course_details_for_instructor,
    update_course as update_course_repo,
)
from ..schemas.course import CourseCreate, CourseUpdate
from ..models.course import Course


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
