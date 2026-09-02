from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    func,
    text,
)

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
    created_by = Column("created_by", Integer, ForeignKey("user.id"))
    created_at = Column(
        "created_at", TIMESTAMP, nullable=False, server_default=func.now()
    )
    updated_by = Column("updated_by", Integer, ForeignKey("user.id"))
    updated_at = Column("updated_at", TIMESTAMP, nullable=True)
