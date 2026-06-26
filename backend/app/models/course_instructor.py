from sqlalchemy import Column, ForeignKey, Integer

from .base import AcademicWritingSchema


class CourseInstructor(AcademicWritingSchema):
    __tablename__ = "course_instructor"

    course_id = Column("course_id", Integer, ForeignKey("course.id"), primary_key=True)
    instructor_id = Column(
        "instructor_id", Integer, ForeignKey("user.id"), primary_key=True
    )
