import secrets
from io import StringIO

import pandas as pd
from fastapi import HTTPException, UploadFile
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ..models.role import Role
from ..models.user import User
from ..models.submission import Submission
from ..repository.role import retrieve_by_id as retrieve_role_by_id, retrieve_by_name
from ..repository.user import retrieve_by_email_from_user
from ..repository.submission import retrieve_by_user_and_chapter
from ..repository.submission_mode import (
    retrieve_by_id as retrieve_submission_mode_by_id,
)
from ..schemas.user import UpdatedUserInfo, UpdatedUserPassword, UserCreate
from ..schemas.submission import SubmissionResponse
from ..utils.auth import get_password_hash
from ..utils.db import add, commit_and_refresh
from ..utils.email import get_email_body, send_email
from ..utils.logger import logger
from ..utils.user import create_user_response

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_user(user: UserCreate, db: Session):
    role: Role = retrieve_role_by_id(db, user)
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
            group_id=None,
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


def batch_users(file: UploadFile, db: Session):
    if file.content_type != "text/csv":
        raise HTTPException(status_code=400, detail="File must be a CSV")

    try:
        logger.info("Reading students from the uploaded csv...")
        df = pd.read_csv(StringIO(file.file.read().decode("utf-8")))
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to parse CSV")

    logger.info("Successfully read students from the uploaded csv")
    required_columns = {"Ime", "Prezime", "Email", "Grupa", "Indeks"}
    if not required_columns.issubset(df.columns):
        raise HTTPException(
            status_code=400,
            detail=f"CSV must contain the following columns: {', '.join(required_columns)}",
        )

    logger.info("Retrieving student role info...")
    student_role = retrieve_by_name(db, "Student")
    if not student_role:
        raise HTTPException(status_code=404, detail="Student role not found")
    logger.info("Successfully retrieved student role info")

    users = []
    logger.info("Creating student objects...")
    for _, row in df.iterrows():
        raw_password = secrets.token_urlsafe(12)
        hashed_password = pwd_context.hash(raw_password)

        user = User(
            email=row["Email"],
            password=hashed_password,
            name=row["Ime"],
            surname=row["Prezime"],
            role_id=student_role.id,
            group_id=int(row["Grupa"]),
            index=row["Indeks"],
        )
        users.append(user)

        email_body = get_email_body(row, raw_password)
        try:
            send_email(
                row["Email"], "[PIGKUT] Kredencijali za pristup platformi", email_body
            )
        except Exception as e:
            logger.info(f"Failed to send email to {row['email']}: {e}")

    db.bulk_save_objects(users)
    db.commit()

    logger.info(f"{len(users)} users imported successfully")


def retrieve_submissions_for_specific_chapter(
    db: Session,
    user: User,
    chapter_id: str,
) -> list[SubmissionResponse]:
    logger.info(
        f"Retrieving submissions for the user {user.id} for the chapter {chapter_id}..."
    )
    submissions: list[Submission] = retrieve_by_user_and_chapter(
        db, user.id, chapter_id
    )
    submission_responses = []
    for submission in submissions:
        submission_responses.append(
            SubmissionResponse(
                id=submission.id,
                text=submission.text,
                gd_file_id=submission.gd_file_id,
                gd_file_link=submission.gd_file_link,
                achieved_points=submission.achieved_points,
                submission_mode=retrieve_submission_mode_by_id(
                    db, submission.submission_mode_id
                ).name,
                submitted_at=submission.submitted_at,
            )
        )
    logger.info("Successfully retrieved submissions")
    return submission_responses
