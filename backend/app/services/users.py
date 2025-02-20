from sqlalchemy.orm import Session
from fastapi import HTTPException

from ..models.user import User
from ..models.role import Role

from ..schemas.users import UserCreate, UpdatedUserInfo, UpdatedUserPassword

from ..utils.auth import get_password_hash
from ..utils.users import create_user_response
from ..utils.db import commit_and_refresh, add
from ..utils.logger import logger

from ..repository.users import retrieve_by_email_from_user
from ..repository.roles import retrieve_by_id


def create_user(user: UserCreate, db: Session):
    role: Role = retrieve_by_id(db, user)
    if not role:
        raise HTTPException(
            status_code=400, detail=f"Role ID {user.role_id} does not exist"
        )
    user_with_same_email: User = retrieve_by_email_from_user(db, user)
    if user_with_same_email:
        raise HTTPException(
            status_code=400,
            detail=f"User with email address {user.email} already exists",
        )
    user = User(
        email=user.email,
        password=get_password_hash(user.password),
        name=user.name,
        surname=user.surname,
        role_id=user.role_id,
    )
    add(db, user)
    commit_and_refresh(db, user)
    return create_user_response(user, role)


def retrieve_logged_in_user(user: User, role: Role):
    return create_user_response(user, role)


def update_user_info(
    user: User, updated_user_info: UpdatedUserInfo, role: Role, db: Session
):
    user.name = updated_user_info.name
    user.surname = updated_user_info.surname
    commit_and_refresh(db, user)
    return create_user_response(user, role)


def update_user_password(
    user: User, updated_password: UpdatedUserPassword, role: Role, db: Session
):
    if updated_password.password != updated_password.confirmed_password:
        raise HTTPException(status_code=400, detail="Passwords aren't matching")
    user.password = get_password_hash(updated_password.password)
    commit_and_refresh(db, user)
    return create_user_response(user, role)


def deactivate_user(user: User, db: Session):
    user.is_active = False
    commit_and_refresh(db, user)
