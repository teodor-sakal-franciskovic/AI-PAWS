from sqlalchemy import TIMESTAMP, Column, Float, ForeignKey, Integer, func

from .base import AcademicWritingSchema


class UserCoursePoints(AcademicWritingSchema):
    __tablename__ = "user_course_points"

    course_id = Column("course_id", Integer, ForeignKey("course.id"), primary_key=True)
    user_id = Column("user_id", Integer, ForeignKey("user.id"), primary_key=True)
    achieved_points = Column("achieved_points", Float)
    max_points = Column("max_points", Float)
    updated_at = Column(
        "updated_at",
        TIMESTAMP,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
