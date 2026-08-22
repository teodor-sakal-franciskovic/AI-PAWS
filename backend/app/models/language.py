from sqlalchemy import Boolean, Column, Integer, String, text

from .base import AcademicWritingSchema


class Language(AcademicWritingSchema):
    __tablename__ = "language"

    id = Column("id", Integer, primary_key=True)
    name = Column("name", String, nullable=False)
    short_name = Column("short_name", String, nullable=False)
    is_active = Column(
        "is_active", Boolean, nullable=False, server_default=text("true")
    )
