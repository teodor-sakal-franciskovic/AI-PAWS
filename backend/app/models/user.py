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


class User(AcademicWritingSchema):
    __tablename__ = "user"

    id = Column("id", Integer, primary_key=True)
    email = Column("email", String, unique=True, index=True)
    index = Column("index", String, unique=True)
    password = Column("password", String)
    is_active = Column("is_active", Boolean, server_default=text("true"))
    name = Column("name", String)
    surname = Column("surname", String)
    role_id = Column("role_id", Integer, ForeignKey("role.id"), nullable=False)
    created_at = Column(
        "created_at", TIMESTAMP, nullable=False, server_default=func.now()
    )
    faculty = Column("faculty", String, nullable=True)
    created_by = Column("created_by", Integer, ForeignKey("user.id"), nullable=True)
