from typing import List

from sqlalchemy.orm import Session

from ..models.submission_mode import SubmissionMode
from ..repository.submission_mode import retrieve_all
from ..schemas.submission_mode import SubmissionModeResponse


def retrieve_submission_modes(db: Session):
    submission_modes: List[SubmissionMode] = retrieve_all(db)
    return [
        SubmissionModeResponse(
            id=submission_mode.id,
            name=submission_mode.name,
            description=submission_mode.description,
        )
        for submission_mode in submission_modes
    ]
