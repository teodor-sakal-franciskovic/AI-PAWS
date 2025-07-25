from sqlalchemy import (
    TIMESTAMP,
    Column,
    ForeignKey,
    Integer,
    String,
    func,
    Boolean,
    text as sqlalchemy_text,
    Float,
)

from .base import AcademicWritingSchema


class Submission(AcademicWritingSchema):
    __tablename__ = "submission"

    id = Column("id", Integer, primary_key=True)
    submitted_at = Column(
        "submitted_at", TIMESTAMP, nullable=False, server_default=func.now()
    )
    text = Column("text", String)
    gd_file_id = Column("gd_file_id", String)
    gd_file_link = Column("gd_file_link", String)
    achieved_points_percentage = Column("achieved_points_percentage", Float)
    user_id = Column("user_id", Integer, ForeignKey("user.id"))
    submission_mode_id = Column("mode_id", Integer)
    graded = Column("graded", Boolean, server_default=sqlalchemy_text("false"))
    assignment_id = Column("assignment_id", Integer, ForeignKey("assignment.id"))
