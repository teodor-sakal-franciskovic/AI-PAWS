from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models.group import Group


def retrieve_all_valid(db: Session):
    return (
        db.query(Group)
        .filter(Group.valid_from <= func.now())
        .filter(Group.valid_until >= func.now())
        .all()
    )
