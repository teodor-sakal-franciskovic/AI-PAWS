from sqlalchemy import (TIMESTAMP, Boolean, Column, ForeignKey, Integer,
                        String, func)

from .base import AcademicWritingSchema


class Feedback(AcademicWritingSchema):
    __tablename__ = "feedback"

    id = Column("id", Integer, primary_key=True)
    text = Column("text", String)
    initially_fulfilled = Column("initially_fulfilled", Boolean, default=True)
    rule_id = Column("rule_id", Integer, ForeignKey("rule.id"))
    fulfillment_id = Column("fulfillment_id", Integer, ForeignKey("fulfillment.id"))
    additional_text = Column("additional_text", String, default="")
    is_valid = Column("is_valid", Boolean, default=True)
    inserted_at = Column("inserted_at", TIMESTAMP, nullable=False, server_default=func.now())
