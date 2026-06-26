from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, text

from .base import AcademicWritingSchema


class Rule(AcademicWritingSchema):
    __tablename__ = "rule"

    id = Column("id", Integer, primary_key=True)
    name = Column("name", String, nullable=False)
    user_description = Column("user_description", String)
    include_in_prompt = Column(
        "include_in_prompt", Boolean, server_default=text("true")
    )
    rule_group_id = Column("rule_group_id", Integer, ForeignKey("rule_group.id"))
    prompt_description = Column("prompt_description", String)
