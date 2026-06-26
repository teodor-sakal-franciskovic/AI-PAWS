from sqlalchemy import Column, Float, ForeignKey, Integer

from .base import AcademicWritingSchema


class UserCoursePoints(AcademicWritingSchema):
    __tablename__ = "user_course_points"

    course_id = Column("course_id", Integer, ForeignKey("course.id"), primary_key=True)
    user_id = Column("user_id", Integer, ForeignKey("user.id"), primary_key=True)
    achieved_points = Column("achieved_points", Float)
