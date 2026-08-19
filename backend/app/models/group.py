from sqlalchemy import TIMESTAMP, Boolean, Column, Integer, String, text

from .base import AcademicWritingSchema


class Group(AcademicWritingSchema):
    __tablename__ = "group"

    id = Column("id", Integer, primary_key=True)
    name = Column("name", String, nullable=False)
    short_name = Column("short_name", String, nullable=True)
    valid_from = Column("valid_from", TIMESTAMP, nullable=False)
    valid_until = Column("valid_until", TIMESTAMP, nullable=False)
    is_deleted = Column(
        "is_deleted", Boolean, nullable=False, server_default=text("false")
    )
