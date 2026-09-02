from pydantic import BaseModel, EmailStr

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
    index: str | None = None
    faculty: str | None = None


class UserSummaryResponse(BaseModel):
    id: int
    name: str
    surname: str

    class Config:
        from_attributes = True


class UpdatedUserInfo(BaseModel):
    name: str
    surname: str


class UpdatedUserPassword(BaseModel):
    password: str
    confirmed_password: str


class EvaluativeUserSubmissionSchema(BaseModel):
    user_id: int
    user_index: str
    name: str
    surname: str
    submissions: list[EvaluativeSubmissionSchema]


class EvaluativeUsersSubmissionResponse(BaseModel):
    users_with_submissions: list[EvaluativeUserSubmissionSchema]
