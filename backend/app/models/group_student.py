from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint

from .base import AcademicWritingSchema


class GroupStudent(AcademicWritingSchema):
    __tablename__ = "group_student"
    __table_args__ = (
        UniqueConstraint(
            "course_id", "student_id", name="uq_group_student_course_student"
        ),
    )

    group_id = Column("group_id", Integer, ForeignKey("group.id"), primary_key=True)
    student_id = Column("student_id", Integer, ForeignKey("user.id"), primary_key=True)
    course_id = Column("course_id", Integer, ForeignKey("course.id"), nullable=False)
