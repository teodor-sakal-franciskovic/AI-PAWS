from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models.prompt_template import PromptTemplate


def retrieve_by_purpose(db: Session, purpose: str):
    return (
        db.query(PromptTemplate)
        .filter(func.lower(PromptTemplate.purpose) == purpose.lower())
        .first()
    )
