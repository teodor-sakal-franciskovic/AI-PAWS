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


class RuleGroup(AcademicWritingSchema):
    __tablename__ = "rule_group"

    id = Column("id", Integer, primary_key=True)
    name = Column("name", String, nullable=False)
    is_active = Column(
        "is_active", Boolean, nullable=False, server_default=text("true")
    )
    created_by = Column("created_by", Integer, ForeignKey("user.id"))
    created_at = Column(
        "created_at", TIMESTAMP, nullable=False, server_default=func.now()
    )
    updated_by = Column("updated_by", Integer, ForeignKey("user.id"))
    updated_at = Column("updated_at", TIMESTAMP, nullable=True)
