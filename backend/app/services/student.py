import re
import secrets

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ..exceptions import ApiError
from ..models.user import User
from ..repository.role import retrieve_by_name as retrieve_role_by_name
from ..repository.student import (
    retrieve_existing_emails,
    retrieve_existing_indexes,
    search_students,
)
from ..schemas.group import GroupStudentResponse
from ..schemas.student import (
    StudentBatchErrorItem,
    StudentBatchItem,
    StudentSearchResponse,
)
from ..utils.email import get_email_body, send_email
from ..utils.logger import logger

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

BATCH_MAX_SIZE = 500
EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _validate_batch(
    students: list[StudentBatchItem], db: Session
) -> list[StudentBatchErrorItem]:
    errors: list[StudentBatchErrorItem] = []

    emails_seen: dict[str, int] = {}
    indexes_seen: dict[str, int] = {}
    for row_number, student in enumerate(students, start=1):
        if not EMAIL_REGEX.match(student.email):
            errors.append(
                StudentBatchErrorItem(
                    row_number=row_number,
                    field="email",
                    code="STUDENT_EMAIL_INVALID",
                    message="Email address is not valid.",
                )
            )

        if student.email in emails_seen:
            errors.append(
                StudentBatchErrorItem(
                    row_number=row_number,
                    field="email",
                    code="STUDENT_EMAIL_DUPLICATED_IN_BATCH",
                    message="Email is duplicated within the request.",
                )
            )
        else:
            emails_seen[student.email] = row_number

        if student.index in indexes_seen:
            errors.append(
                StudentBatchErrorItem(
                    row_number=row_number,
                    field="index",
                    code="STUDENT_INDEX_DUPLICATED_IN_BATCH",
                    message="Index is duplicated within the request.",
                )
            )
        else:
            indexes_seen[student.index] = row_number

    existing_emails = retrieve_existing_emails(db, list(emails_seen.keys()))
    existing_indexes = retrieve_existing_indexes(db, list(indexes_seen.keys()))

    for email, row_number in emails_seen.items():
        if email in existing_emails:
            errors.append(
                StudentBatchErrorItem(
                    row_number=row_number,
                    field="email",
                    code="STUDENT_EMAIL_ALREADY_EXISTS",
                    message="A student with this email already exists.",
                )
            )

    for index, row_number in indexes_seen.items():
        if index in existing_indexes:
            errors.append(
                StudentBatchErrorItem(
                    row_number=row_number,
                    field="index",
                    code="STUDENT_INDEX_ALREADY_EXISTS",
                    message="A student with this index already exists.",
                )
            )

    return errors


def register_students(
    students: list[StudentBatchItem], db: Session, created_by: int
) -> int:
    if not students:
        raise ApiError(400, "STUDENT_BATCH_EMPTY", "The students array is empty.")
    if len(students) > BATCH_MAX_SIZE:
        raise ApiError(
            400,
            "STUDENT_BATCH_LIMIT_EXCEEDED",
            f"A batch can contain at most {BATCH_MAX_SIZE} students.",
        )

    errors = _validate_batch(students, db)
    if errors:
        raise ApiError(
            400,
            "STUDENT_BATCH_VALIDATION_FAILED",
            "Student batch contains validation errors.",
            data={"errors": [e.model_dump() for e in errors]},
        )

    student_role = retrieve_role_by_name(db, "Student")
    if not student_role:
        raise ApiError(500, "INTERNAL_ERROR", "Student role not found.")

    created: list[tuple[User, str]] = []
    for student in students:
        raw_password = secrets.token_urlsafe(12)
        hashed_password = pwd_context.hash(raw_password)
        user = User(
            email=student.email,
            password=hashed_password,
            name=student.name,
            surname=student.surname,
            faculty=student.faculty,
            index=student.index,
            role_id=student_role.id,
            group_id=None,
            created_by=created_by,
        )
        created.append((user, raw_password))

    try:
        db.bulk_save_objects([user for user, _ in created])
        db.commit()
    except Exception as e:
        db.rollback()
        raise ApiError(
            400,
            "VALIDATION_ERROR",
            f"Something went wrong while writing the students to the database: {e}",
        )

    logger.info(f"{len(created)} students registered successfully")
    for user, raw_password in created:
        email_body = get_email_body({"Ime": user.name, "Email": user.email}, raw_password)
        try:
            send_email(
                user.email,
                "[PIGKUT] Kredencijali za pristup platformi",
                email_body,
            )
        except Exception as e:
            logger.info(f"Failed to send email to {user.email}: {e}")

    return len(created)


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
