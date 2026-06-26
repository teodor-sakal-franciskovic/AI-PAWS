from sqlalchemy import Column, Integer, ForeignKey

from .base import AcademicWritingSchema


class CourseGroup(AcademicWritingSchema):
    __tablename__ = "course_group"

    course_id = Column("course_id", Integer, ForeignKey("course.id"), primary_key=True)
    group_id = Column("group_id", Integer, ForeignKey("group.id"), primary_key=True)
