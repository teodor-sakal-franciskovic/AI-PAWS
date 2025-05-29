from sqlalchemy import Column, ForeignKey, Integer, String

from .base import AcademicWritingSchema


class Fulfillment(AcademicWritingSchema):
    __tablename__ = "fulfillment"

    id = Column("id", Integer, primary_key=True)
    fulfillment_value = Column("fulfillment_value", Integer)  # 0, 1, 2
    rule_id = Column("rule_id", Integer, ForeignKey("rule.id"))
    submission_id = Column("submission_id", Integer, ForeignKey("submission.id"))
