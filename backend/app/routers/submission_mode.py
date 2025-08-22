from typing import List

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..dependencies.db import get_db
from ..dependencies.submission_mode import get_retrieve_submission_modes
from ..schemas.response import GenericResponse
from ..schemas.submission_mode import SubmissionModeResponse

router = APIRouter(
    prefix="/submission-modes",
    tags=["submission-modes"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", tags=["submission-modes"], response_model=GenericResponse)
def retrieve_submission_modes(
    db: Session = Depends(get_db),
    retrieve_submission_modes=Depends(get_retrieve_submission_modes),
) -> GenericResponse:
    submission_modes: List[SubmissionModeResponse] = retrieve_submission_modes(db)
    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message="Successfully retrieved submission_modes", data=submission_modes
        ).model_dump(),
    )
