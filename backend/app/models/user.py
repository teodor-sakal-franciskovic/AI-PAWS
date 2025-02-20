from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    LargeBinary,
    ForeignKey,
)
from .base import BaseSchema


class User(BaseSchema):
    __tablename__ = "users"

    id = Column("id", Integer, primary_key=True)
    email = Column("email", String, unique=True, index=True)
    password = Column("password", String)
    is_active = Column("is_active", Boolean, default=True)
    name = Column("name", String)
    surname = Column("surname", String)
    role_id = Column("role_id", Integer, ForeignKey("roles.id"), nullable=False)
