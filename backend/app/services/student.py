import secrets
from io import StringIO

import pandas as pd
from fastapi import UploadFile
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ..exceptions import ApiError
from ..models.role import Role
from ..models.user import User
from ..repository.role import retrieve_by_name as retrieve_role_by_name
from ..repository.student import search_students
from ..schemas.group import GroupStudentResponse
from ..schemas.student import StudentSearchResponse
from ..utils.email import get_email_body, send_email
from ..utils.logger import logger

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

BATCH_REQUIRED_COLUMNS = {"Email", "Ime", "Prezime", "Fakultet", "Indeks"}


def _parse_batch_csv(file: UploadFile) -> pd.DataFrame:
    if file.content_type != "text/csv":
        raise ApiError(400, "VALIDATION_ERROR", "File must be a CSV.")
    try:
        logger.info("Reading students from the uploaded csv...")
        df = pd.read_csv(StringIO(file.file.read().decode("utf-8")))
        logger.info("Successfully read students from the uploaded csv")
    except Exception:
        raise ApiError(400, "VALIDATION_ERROR", "Failed to parse CSV.")

    if not BATCH_REQUIRED_COLUMNS.issubset(df.columns):
        raise ApiError(
            400,
            "VALIDATION_ERROR",
            f"CSV must contain the following columns: {', '.join(BATCH_REQUIRED_COLUMNS)}",
        )
    return df


def _create_student_objects(df: pd.DataFrame, role: Role) -> list[tuple[User, dict]]:
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
            faculty=row["Fakultet"],
            index=row["Indeks"],
            role_id=role.id,
            group_id=None,
        )
        users.append((user, {"row": row, "raw_password": raw_password}))
    return users


def _persist_batch_students(db: Session, users: list[tuple[User, dict]]) -> None:
    try:
        db.bulk_save_objects([user for user, _ in users])
        db.commit()
    except Exception as e:
        db.rollback()
        raise ApiError(
            400,
            "VALIDATION_ERROR",
            f"Something went wrong while writing the students to the database: {e}",
        )


def _send_batch_emails(users: list[tuple[User, dict]]) -> None:
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


def register_students(file: UploadFile, db: Session) -> int:
    df = _parse_batch_csv(file)

    student_role = retrieve_role_by_name(db, "Student")
    if not student_role:
        raise ApiError(500, "INTERNAL_ERROR", "Student role not found.")

    users = _create_student_objects(df, student_role)
    _persist_batch_students(db, users)

    logger.info(f"{len(users)} students registered successfully")
    _send_batch_emails(users)
    return len(users)


def search_students_service(
    db: Session,
    email: str | None,
    name: str | None,
    surname: str | None,
    faculty: str | None,
    index: str | None,
    page: int,
    page_size: int,
) -> StudentSearchResponse:
    student_role = retrieve_role_by_name(db, "Student")
    if not student_role:
        raise ApiError(500, "INTERNAL_ERROR", "Student role not found.")

    items, total = search_students(
        db, student_role.id, email, name, surname, faculty, index, page, page_size
    )
    return StudentSearchResponse(
        items=[GroupStudentResponse.model_validate(u) for u in items],
        total=total,
        page=page,
        page_size=page_size,
    )
