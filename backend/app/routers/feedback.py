from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..dependencies.auth import get_current_active_user, require_role
from ..dependencies.db import get_db
from ..dependencies.llm import initialise_llm

from ..services.historical_profile import (
    retrieve_latest_historical_profile_snapshot,
    insert_historical_profile_snapshot,
)
from ..services.submission import retrieve_submission
from ..services.feedback import (
    retrieve_feedback,
    request_additional_interactive_feedback,
    update_feedback_with_additional_context,
    invalidate_feedback,
)

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
def request_additional_feedback_endpoint(
    feedback_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
    llm=Depends(initialise_llm),
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
        update_feedback_with_additional_context(
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
def invalidate_feedback_endpoint(
    feedback_id: int,
    role: Annotated[Role, Depends(require_role("Student"))],
    db: Session = Depends(get_db),
):
    invalidate_feedback(db, feedback_id)
    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message=f"Successfully invalidated feedback with id {feedback_id}.",
            data=None,
        ).model_dump(),
    )
