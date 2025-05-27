from sqlalchemy.orm import Session

from ..schemas.user import UserCreate

from ..models.user import User


def retrieve_by_email_from_user(db: Session, user: UserCreate):
    return db.query(User).filter(User.email == user.email).first()


def retrieve_by_email(db: Session, username: str):
    return db.query(User).filter(User.email == username).first()
