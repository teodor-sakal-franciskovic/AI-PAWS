from sqlalchemy.orm import Session

from ..models.historical_profile import HistoricalProfile


def retrieve_latest(db: Session, user_id: int):
    return (
        db.query(HistoricalProfile)
        .filter(HistoricalProfile.user_id == user_id)
        .order_by(HistoricalProfile.inserted_at.desc())
        .first()
    )
