from sqlalchemy import Column, ForeignKey, Integer

from .base import AcademicWritingSchema


class CourseStudentInstructor(AcademicWritingSchema):
    __tablename__ = "course_student_instructor"

    course_id = Column("course_id", Integer, ForeignKey("course.id"), primary_key=True)
    student_id = Column("student_id", Integer, ForeignKey("user.id"), primary_key=True)
    instructor_id = Column(
        "instructor_id", Integer, ForeignKey("user.id"), nullable=False
    )
