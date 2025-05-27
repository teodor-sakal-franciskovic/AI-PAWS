from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..models.role import Role
from ..models.user import User
from ..repository.roles import retrieve_by_id
from ..repository.users import retrieve_by_email_from_user
from ..schemas.users import UpdatedUserInfo, UpdatedUserPassword, UserCreate
from ..utils.auth import get_password_hash
from ..utils.db import add, commit_and_refresh
from ..utils.logger import logger
from ..utils.users import create_user_response


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
    try:
        user = User(
            email=user.email,
            password=get_password_hash(user.password),
            name=user.name,
            surname=user.surname,
            role_id=user.role_id,
            group_id=None
        )
        add(db, user)
        commit_and_refresh(db, user)
    except Exception as e:
        logger.info(f"e {e}")
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
