import secrets
from io import StringIO
from typing import List

import pandas as pd
from fastapi import HTTPException, UploadFile
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ..models.role import Role
from ..models.user import User
from ..models.submission import Submission

from ..repository.role import (
    retrieve_by_id as retrieve_role_by_id,
    retrieve_by_name as retrieve_role_by_name,
)
from ..repository.user import (
    retrieve_by_email_from_user,
    retrieve_evaluative_submissions,
    retrieve_by_id as retrieve_user_by_id_db,
)
from ..repository.submission import update_grade
from ..repository.submission_mode import (
    retrieve_by_name as retrieve_submission_mode_by_name,
)
from ..repository.feedback import update_final_feedback_text
from ..repository.fulfillment import update_final_fulfillment_value
from ..schemas.user import (
    UpdatedUserInfo,
    UpdatedUserPassword,
    UserCreate,
)
from ..schemas.submission import (
    TAEvaluationGradesRequest,
    TAEvaluationGrade,
)
from ..utils.auth import get_password_hash
from ..utils.db import add, commit_and_refresh
from ..utils.email import get_email_body, send_email
from ..utils.logger import logger
from ..utils.user import create_user_response, group_submission_data

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
            assigned_to_ta=None,
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


def _parse_batch_csv(file: UploadFile) -> pd.DataFrame:
    if file.content_type != "text/csv":
        raise HTTPException(status_code=400, detail="File must be a CSV")
    try:
        logger.info("Reading students from the uploaded csv...")
        df = pd.read_csv(StringIO(file.file.read().decode("utf-8")))
        logger.info("Successfully read students from the uploaded csv")
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to parse CSV")

    required_columns = {"Ime", "Prezime", "Email", "Grupa", "Indeks", "Asistent"}
    if not required_columns.issubset(df.columns):
        raise HTTPException(
            status_code=400,
            detail=f"CSV must contain the following columns: {', '.join(required_columns)}",
        )
    return df


def _create_batch_user_objects(df: pd.DataFrame, role: Role) -> List[tuple[User, dict]]:
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
            role_id=role.id,
            group_id=int(row["Grupa"]),
            index=row["Indeks"],
            assigned_to_ta=row["Asistent"],
        )
        users.append((user, {"row": row, "raw_password": raw_password}))
    return users


def _send_batch_emails(users: List[tuple[User, dict]]):
    for _, meta in users:
        email_body = get_email_body(meta["row"], meta["raw_password"])
        try:
            send_email(
                meta["row"]["Email"],
                "[PIGKUT] Kredencijali za pristup platformi",
                email_body,
            )
        except Exception as e:
            logger.info(f"Failed to send email to {meta['row']['Email']}: {e}")


def batch_users(file: UploadFile, db: Session):
    df = _parse_batch_csv(file)

    student_role = retrieve_role_by_name(db, "Student")
    if not student_role:
        raise HTTPException(status_code=404, detail="Student role not found")

    users = _create_batch_user_objects(df, student_role)

    try:
        db.bulk_save_objects([user for user, _ in users])
        db.commit()
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Something went wrong while writing the students to the database: {e}",
        )

    logger.info(f"{len(users)} users imported successfully")
    _send_batch_emails(users)


def retrieve_evaluative_submissions_for_ta_students(db: Session, ta: User):
    evaluative_submission_mode: Submission = retrieve_submission_mode_by_name(
        db, "Evaluative mode"
    )
    submissions = retrieve_evaluative_submissions(
        db, ta.id, evaluative_submission_mode.id
    )
    return group_submission_data(submissions)


def _calculate_achieved_percentage(grades: List[TAEvaluationGrade]) -> float:
    max_points = 2 * len(grades)
    achieved_points = sum(grade.final_grade for grade in grades)
    return achieved_points / max_points


def grade_submission(
    db: Session, submission_id: int, ta_evaluation_grades: TAEvaluationGradesRequest
):
    grades: List[TAEvaluationGrade] = ta_evaluation_grades.evaluation_grades
    for grade in grades:
        update_final_feedback_text(db, grade.feedback_id, grade.final_feedback)
        update_final_fulfillment_value(db, grade.fulfillment_id, grade.final_grade)
    achieved_points_percentage = _calculate_achieved_percentage(grades)
    update_grade(db, submission_id, achieved_points_percentage)


def retrieve_user_by_id(db: Session, id: int) -> User:
    return retrieve_user_by_id_db(db, id)


def read_pretest_results(file: UploadFile) -> pd.DataFrame:
    if file.content_type != "text/csv":
        raise HTTPException(status_code=400, detail="File must be a CSV")
    try:
        logger.info("Reading pretest results from the uploaded csv...")
        df = pd.read_csv(StringIO(file.file.read().decode("utf-8")))
        logger.info("Successfully read pretest results from the uploaded csv")
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to parse CSV")
    return df
