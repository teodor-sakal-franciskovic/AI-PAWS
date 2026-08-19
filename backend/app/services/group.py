from fastapi import HTTPException, UploadFile, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..models.group import Group
from ..repository.group import (
    retrieve_all_valid,
    retrieve_by_id,
    retrieve_groups_grouped_by_course,
    retrieve_students_in_group,
    set_user_group,
    soft_delete_group,
    update_group,
)
from ..repository.user import retrieve_by_id as retrieve_user_by_id
from ..schemas.group import (
    GroupCreate,
    GroupResponse,
    GroupStudentResponse,
    GroupUpdate,
)
from ..services.user import batch_users_for_group
from ..utils.logger import logger


def create_group(group: GroupCreate, db: Session):
    try:
        logger.info(f"Creating a group with the received object: {group} ")
        db_group = Group(
            name=group.name,
            valid_from=group.valid_from,
            valid_until=group.valid_until,
        )
        logger.info("Adding the group to the DB")
        db.add(db_group)
        logger.info("Committing...")
        db.commit()
        logger.info("Refreshing...")
        db.refresh(db_group)

    except IntegrityError as e:
        db.rollback()
        logger.warning(f"IntegrityError while storing group {group}: {e}")
        if "duplicate key value violates unique constraint" in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A group with name '{group.name}' already exists.",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database integrity error occurred.",
        )

    except Exception as e:
        logger.info(
            f"An expection occurred while storing the group {group} to the database: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while storing the group to the database.",
        )
    logger.info(f"Successfully created the group: {db_group}")


def retrieve_active_groups(db: Session) -> list[GroupResponse]:
    groups: list[Group] = retrieve_all_valid(db)
    return [
        GroupResponse(
            id=group.id,
            name=group.name,
            valid_from=group.valid_from,
            valid_until=group.valid_until,
        )
        for group in groups
    ]


def get_groups_for_instructor(db: Session, user_id: int) -> list[dict]:
    return retrieve_groups_grouped_by_course(db, user_id)


def modify_group(db: Session, group_id: int, data: GroupUpdate) -> Group:
    group = retrieve_by_id(db, group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found.",
        )
    try:
        return update_group(db, group, data)
    except IntegrityError as e:
        db.rollback()
        logger.warning(f"IntegrityError while updating group {group_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A group with that name already exists.",
        )


def remove_group(db: Session, group_id: int) -> None:
    group = retrieve_by_id(db, group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found.",
        )
    soft_delete_group(db, group)


def _get_group_or_404(db: Session, group_id: int) -> Group:
    group = retrieve_by_id(db, group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Group not found."
        )
    return group


def get_students_in_group(db: Session, group_id: int) -> list[GroupStudentResponse]:
    _get_group_or_404(db, group_id)
    students = retrieve_students_in_group(db, group_id)
    return [GroupStudentResponse.model_validate(s) for s in students]


def move_student_to_group(db: Session, group_id: int, user_id: int) -> None:
    _get_group_or_404(db, group_id)
    user = retrieve_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )
    set_user_group(db, user, group_id)


def remove_student_from_group(db: Session, group_id: int, user_id: int) -> None:
    _get_group_or_404(db, group_id)
    user = retrieve_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )
    if user.group_id != group_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not belong to this group.",
        )
    set_user_group(db, user, None)


def import_students_into_group(db: Session, group_id: int, file: UploadFile) -> int:
    _get_group_or_404(db, group_id)
    return batch_users_for_group(file, group_id, db)
