from sqlalchemy import Column, Integer, String
from .base import BaseSchema


class Role(BaseSchema):
    __tablename__ = "roles"

    id = Column("id", Integer, primary_key=True)
    name = Column("name", String, nullable=False)
