from sqlalchemy import Column, ForeignKey, Integer

from .base import AcademicWritingSchema


class Fulfillment(AcademicWritingSchema):
    __tablename__ = "fulfillment"

    id = Column("id", Integer, primary_key=True)
    initial_fulfillment_value = Column("initial_fulfillment_value", Integer)  # 0, 1, 2
    final_fulfillment_value = Column("final_fulfillment_value", Integer)
    feedback_id = Column("feedback_id", Integer, ForeignKey("feedback.id"))
    submission_id = Column("submission_id", Integer, ForeignKey("submission.id"))
