from sqlalchemy import TIMESTAMP, Column, Integer, String, ForeignKey

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
    chapter_id = Column("chapter_id", Integer, ForeignKey("chapter.id"))
