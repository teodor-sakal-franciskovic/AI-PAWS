from sqlalchemy.orm import Session

from ..repository.course import create_and_populate_course
from ..schemas.course import CourseCreate
from ..models.course import Course


def create_course(db: Session, data: CourseCreate) -> Course:
    return create_and_populate_course(db, data)
