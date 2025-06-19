from sqlalchemy import Column, ForeignKey, Integer

from .base import AcademicWritingSchema


class Fulfillment(AcademicWritingSchema):
    __tablename__ = "fulfillment"

    id = Column("id", Integer, primary_key=True)
    fulfillment_value = Column("fulfillment_value", Integer)  # 0, 1, 2
    feedback_id = Column("feedback_id", Integer, ForeignKey("feedback.id"))
    submission_id = Column("submission_id", Integer, ForeignKey("submission.id"))
