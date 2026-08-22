from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    func,
    text,
)

from .base import AcademicWritingSchema


class Course(AcademicWritingSchema):
    __tablename__ = "course"

    id = Column("id", Integer, primary_key=True)
    name = Column("name", String, nullable=False)
    max_amount_of_points = Column("max_amount_of_points", Float)
    feedback_language_id = Column(
        "feedback_language_id", Integer, ForeignKey("language.id")
    )
    start_date = Column("start_date", TIMESTAMP, nullable=False)
    end_date = Column("end_date", TIMESTAMP, nullable=False)
    is_active = Column(
        "is_active", Boolean, nullable=False, server_default=text("true")
    )
    created_by = Column("created_by", Integer, ForeignKey("user.id"))
    created_at = Column(
        "created_at", TIMESTAMP, nullable=False, server_default=func.now()
    )
    updated_by = Column("updated_by", Integer, ForeignKey("user.id"))
    updated_at = Column("updated_at", TIMESTAMP, nullable=True, onupdate=func.now())
