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


class Feedback(AcademicWritingSchema):
    __tablename__ = "feedback"

    id = Column("id", Integer, primary_key=True)
    feedback_text = Column("feedback_text", String)
    initially_fulfilled = Column(
        "initially_fulfilled", Boolean, server_default=text("true")
    )
    rule_id = Column("rule_id", Integer, ForeignKey("rule.id"))
    fulfillment_id = Column("fulfillment_id", Integer, ForeignKey("fulfillment.id"))
    additional_text = Column("additional_text", String, server_default="")
    is_valid = Column("is_valid", Boolean, server_default=text("true"))
    inserted_at = Column(
        "inserted_at", TIMESTAMP, nullable=False, server_default=func.now()
    )
    additional_text = Column("additional_text", String, server_default="")
