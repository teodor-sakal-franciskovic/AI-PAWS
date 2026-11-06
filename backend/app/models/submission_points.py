from sqlalchemy import TIMESTAMP, Column, Float, ForeignKey, Integer, func

from .base import AcademicWritingSchema


class SubmissionPoints(AcademicWritingSchema):
    __tablename__ = "submission_points"

    submission_id = Column(
        "submission_id", Integer, ForeignKey("submission.id"), primary_key=True
    )
    max_points = Column("max_points", Float)
    ai_suggested_points = Column("ai_suggested_points", Float)
    final_points = Column("final_points", Float)
    updated_at = Column(
        "updated_at",
        TIMESTAMP,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
