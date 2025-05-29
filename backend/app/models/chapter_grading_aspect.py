from sqlalchemy import Column, ForeignKey, Integer

from .base import AcademicWritingSchema


class ChapterGradingAspect(AcademicWritingSchema):
    __tablename__ = "chapter_grading_aspect"

    chapter_id = Column(
        "chapter_id", Integer, ForeignKey("chapter.id"), primary_key=True
    )
    grading_aspect_id = Column(
        "grading_aspect_id", Integer, ForeignKey("grading_aspect.id"), primary_key=True
    )
