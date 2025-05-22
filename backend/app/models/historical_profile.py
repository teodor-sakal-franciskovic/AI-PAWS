from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, String, func

from .base import AcademicWritingSchema


class HistoricalProfile(AcademicWritingSchema):
    __tablename__ = "historical_profile"

    id = Column("id", Integer, primary_key=True)
    user_id = Column("user_id", Integer, ForeignKey("user.id"))
    summary = Column("summary", String)
    submission_id = Column("submission_id", Integer, ForeignKey("submission.id"))
    inserted_at = Column("inserted_at", TIMESTAMP, nullable=False, server_default=func.now())