from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..dependencies.auth import get_current_active_user, require_role
from ..dependencies.db import get_db
from ..dependencies.llm import initialise_llm
from ..dependencies.historical_profile import (
    get_retrieve_latest_historical_profile_snapshot,
)
from ..dependencies.submission import get_retrieve_submission
from ..dependencies.feedback import (
    get_retrieve_feedback,
    get_request_additional_interactive_feedback,
    get_update_feedback_with_additional_text,
    get_invalidate_feedback,
)

from ..dependencies.historical_profile import get_insert_historical_profile_snapshot

from ..llm.schema import LLMAdditionalFeedbackResponse
from ..schemas.response import GenericResponse
from ..schemas.feedback import InteractiveFeedbackResponse

from ..models.user import User
from ..models.role import Role
from ..models.submission import Submission
from ..models.historical_profile import HistoricalProfile
from ..models.feedback import Feedback

router = APIRouter(
    prefix="/feedbacks",
    tags=["feedbacks"],
    responses={404: {"description": "Not found"}},
)


@router.post("/{feedback_id}/additional", response_model=GenericResponse)
def request_additional_feedback(
    feedback_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
    llm=Depends(initialise_llm),
    retrieve_latest_historical_profile_snapshot=Depends(
        get_retrieve_latest_historical_profile_snapshot
    ),
    retrieve_submission=Depends(get_retrieve_submission),
    retrieve_feedback=Depends(get_retrieve_feedback),
    request_additional_interactive_feedback=Depends(
        get_request_additional_interactive_feedback
    ),
    insert_historical_profile_snapshot=Depends(get_insert_historical_profile_snapshot),
    update_feedback_with_additional_text=Depends(
        get_update_feedback_with_additional_text
    ),
):
    latest_historical_profile: HistoricalProfile = (
        retrieve_latest_historical_profile_snapshot(db, current_user)
    )
    submission: Submission = retrieve_submission(
        db, latest_historical_profile.submission_id
    )
    feedback: Feedback = retrieve_feedback(db, feedback_id)
    llm_additional_feedback_response: LLMAdditionalFeedbackResponse = (
        request_additional_interactive_feedback(
            db, llm, latest_historical_profile, submission, feedback
        )
    )

    updated_feedback: InteractiveFeedbackResponse = (
        update_feedback_with_additional_text(
            db, feedback.id, llm_additional_feedback_response.additional_explanation
        )
    )

    insert_historical_profile_snapshot(
        db, current_user, submission, llm_additional_feedback_response.updated_knowledge
    )

    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message=f"Successfully provided additional feedback for the feedback with id {feedback_id}.",
            data=updated_feedback,
        ).model_dump(),
    )


@router.put("/{feedback_id}/invalid", response_model=GenericResponse)
def invalidate_feedback(
    feedback_id: int,
    role: Annotated[Role, Depends(require_role("Student"))],
    db: Session = Depends(get_db),
    invalidate_feedback=Depends(get_invalidate_feedback),
):
    invalidate_feedback(db, feedback_id)
    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message=f"Successfully invalidated feedback with id {feedback_id}.",
            data=None,
        ).model_dump(),
    )
