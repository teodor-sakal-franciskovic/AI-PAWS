from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session


def commit_and_refresh(
    db: Session, obj, detail="Something went wrong while saving the changes"
):
    try:
        db.commit()
        db.refresh(obj)
    except Exception:
        raise HTTPException(status_code=500, detail=detail)


def add(db: Session, object: Any):
    db.add(object)
