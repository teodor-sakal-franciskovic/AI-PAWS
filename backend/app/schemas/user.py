from pydantic import BaseModel, EmailStr
from typing import List

from .submission import EvaluativeSubmissionSchema


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    surname: str
    role_id: int


class UserResponse(BaseModel):
    email: str
    is_active: bool
    name: str
    surname: str
    role: str


class UpdatedUserInfo(BaseModel):
    name: str
    surname: str


class UpdatedUserPassword(BaseModel):
    password: str
    confirmed_password: str


class EvaluativeUserSubmissionResponse(BaseModel):
    user_id: int
    user_index: str
    name: str
    surname: str
    submissions: List[EvaluativeSubmissionSchema]
