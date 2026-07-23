from sqlalchemy import TIMESTAMP, Column, Float, Integer, String, ForeignKey

from .base import AcademicWritingSchema


class Assignment(AcademicWritingSchema):
    __tablename__ = "assignment"

    id = Column("id", Integer, primary_key=True)
    name = Column("name", String, nullable=False)
    start_date = Column("start_date", TIMESTAMP, nullable=False)
    end_date = Column("end_date", TIMESTAMP, nullable=False)
    submission_mode_id = Column(
        "submission_mode_id", Integer, ForeignKey("submission_mode.id")
    )
    course_id = Column("course_id", Integer, ForeignKey("course.id"))
    percentage_of_points_in_course = Column("percentage_of_points_in_course", Float)
