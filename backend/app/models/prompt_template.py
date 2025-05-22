from sqlalchemy import Column, Integer, String

from .base import AcademicWritingSchema


class PromptTemplate(AcademicWritingSchema):
    __tablename__ = "prompt_template"

    id = Column("id", Integer, primary_key=True)
    text = Column("text", String)
    description = Column("description", String)
