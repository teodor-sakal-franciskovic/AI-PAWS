from sqlalchemy import Column, Integer, String

from .base import AcademicWritingSchema


class PromptTemplate(AcademicWritingSchema):
    __tablename__ = "prompt_template"

    id = Column("id", Integer, primary_key=True)
    system_text = Column("system_text", String)
    user_text = Column("user_text", String)
    description = Column("description", String)
    purpose = Column("purpose", String)
