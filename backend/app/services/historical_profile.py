from sqlalchemy.orm import Session
from ..models.user import User
from ..models.submission import Submission
from ..models.historical_profile import HistoricalProfile
from ..utils.logger import logger


def insert_historical_profile_snapshot(
    db: Session, user: User, submission: Submission, updated_knowledge: str
):
    logger.info(f"Inserting historical profile snapshot for user {user.id}")
    historical_profile = HistoricalProfile(
        user_id=user.id,
        summary=updated_knowledge,
        submission_id=submission.id,
    )
    db.add(historical_profile)
    db.commit()
    logger.info("Successfully inserted historical profile snapshot")
