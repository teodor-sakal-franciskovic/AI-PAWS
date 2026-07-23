from sqlalchemy import Column, ForeignKey, Integer

from .base import AcademicWritingSchema


class CourseSubmissionLanguage(AcademicWritingSchema):
    __tablename__ = "course_submission_language"

    course_id = Column("course_id", Integer, ForeignKey("course.id"), primary_key=True)
    language_id = Column(
        "language_id", Integer, ForeignKey("language.id"), primary_key=True
    )
