from sqlalchemy import Column, ForeignKey, Integer, String, TIMESTAMP, func

from .base import AcademicWritingSchema


class RuleGroup(AcademicWritingSchema):
    __tablename__ = "rule_group"

    id = Column("id", Integer, primary_key=True)
    name = Column("name", String, nullable=False)
    created_by = Column("created_by", Integer, ForeignKey("user.id"))
    created_at = Column(
        "created_at", TIMESTAMP, nullable=False, server_default=func.now()
    )
    updated_by = Column("updated_by", Integer, ForeignKey("user.id"))
    updated_at = Column("updated_at", TIMESTAMP, nullable=True)
