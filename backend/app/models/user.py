from sqlalchemy import (TIMESTAMP, Boolean, Column, ForeignKey, Integer,
                        String, func)

from .base import AcademicWritingSchema


class User(AcademicWritingSchema):
    __tablename__ = "user"

    id = Column("id", Integer, primary_key=True)
    email = Column("email", String, unique=True, index=True)
    password = Column("password", String)
    is_active = Column("is_active", Boolean, default=True)
    name = Column("name", String)
    surname = Column("surname", String)
    role_id = Column("role_id", Integer, ForeignKey("role.id"), nullable=False)
    created_at = Column("created_at", TIMESTAMP, nullable=False, server_default=func.now())
    group_id = Column("group_id", Integer, ForeignKey("group.id"), nullable=True)
