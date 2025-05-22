from sqlalchemy import Column, ForeignKey, Integer

from .base import AcademicWritingSchema


class RuleFeedbackSubmission(AcademicWritingSchema):
    __tablename__ = "rule_feedback_submission"

    rule_id = Column("rule_id", Integer, ForeignKey("rule.id"), primary_key=True)
    submission_id = Column("submission_id", Integer, ForeignKey("submission.id"), primary_key=True)
    feedback_id = Column("feedback_id", Integer, ForeignKey("feedback.id"), primary_key=True)
