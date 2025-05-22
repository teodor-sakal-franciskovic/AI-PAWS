from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, String, func

from .base import AcademicWritingSchema


class Submission(AcademicWritingSchema):
    __tablename__ = "submission"

    id = Column("id", Integer, primary_key=True)
    submitted_at = Column("submitted_at", TIMESTAMP, nullable=False, server_default=func.now())
    text = Column("text", String)
    summary = Column("summary", String)
    file_name = Column("file_name", String)
    achieved_points = Column("achieved_points", Integer)
    user_id = Column("user_id", Integer, ForeignKey("user.id"))
    chapter_id = Column("chapter_id", Integer, ForeignKey("chapter.id"))
    submission_mode_id = Column("mode_id", Integer)