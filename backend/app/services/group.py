from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..models.group import Group
from ..schemas.group import GroupCreate
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
