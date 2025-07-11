from typing import Annotated, List

import anyio
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..dependencies.auth import get_current_active_user
from ..dependencies.chapter import get_extract_chapter_text, get_extract_pdf_to_markdown
from ..dependencies.db import get_db
from ..dependencies.feedback import (
    get_request_initial_interactive_feedback,
    get_create_feedback_objects_for_interactive_mode,
    get_request_evaluation,
    get_create_feedback_objects_for_evaluative_mode,
)
from ..dependencies.google_drive import get_drive_service, get_upload_pdf
from ..dependencies.llm import initialise_llm
from ..dependencies.submission import get_save_submission
from ..dependencies.historical_profile import get_insert_historical_profile_snapshot
from ..dependencies.chapter import get_retrieve_chapters
from ..models.submission import Submission
from ..models.user import User
from ..schemas.response import GenericResponse
from ..schemas.feedback import InteractiveFeedbackResponse
from ..schemas.chapter import ChapterResponse
from ..llm.schema import LLMFeedbackResponse, LLMEvaluationResponse

router = APIRouter(
    prefix="/chapters",
    tags=["chapters"],
    responses={404: {"description": "Not found"}},
)


# TODO: Da li promeniti na id?
@router.post(
    "/{chapter_name}/interactive", response_model=GenericResponse
)  # problem, teorijske osnove, resenje, rezultati
def upload_chapter_interactive(
    chapter_name: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
    llm=Depends(initialise_llm),
    drive_service=Depends(get_drive_service),
    upload_pdf_to_drive=Depends(get_upload_pdf),
    extract_pdf_to_markdown=Depends(get_extract_pdf_to_markdown),
    extract_chapter_text=Depends(get_extract_chapter_text),
    save_submission=Depends(get_save_submission),
    request_initial_interactive_feedback=Depends(
        get_request_initial_interactive_feedback
    ),
    create_feedback_objects_for_interactive_mode=Depends(
        get_create_feedback_objects_for_interactive_mode
    ),
    insert_historical_profile_snapshot=Depends(get_insert_historical_profile_snapshot),
    file: UploadFile = File(...),
):
    file_bytes = anyio.run(file.read)
    # file_id, file_link = upload_pdf_to_drive(
    #    drive_service, file_bytes, current_user, chapter_name, "interaktivni"
    # )
    file_id = "random_id"
    file_link = "random_link"
    markdown_text = extract_pdf_to_markdown(file_bytes)
    extracted_text = extract_chapter_text(markdown_text, chapter_name, db)
    submission: Submission = save_submission(
        db,
        file_id,
        file_link,
        extracted_text,
        chapter_name,
        "Interaktivni mod",
        current_user.id,
    )
    llm_feedback_response: LLMFeedbackResponse = request_initial_interactive_feedback(
        db, llm, submission, current_user, chapter_name
    )

    feedbacks: list[InteractiveFeedbackResponse] = (
        create_feedback_objects_for_interactive_mode(
            db, llm_feedback_response.feedback, chapter_name, submission
        )
    )

    insert_historical_profile_snapshot(
        db, current_user, submission, llm_feedback_response.updated_knowledge
    )

    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message=f"Chapter '{chapter_name}' processed successfully.",
            data=feedbacks,
        ).model_dump(),
    )


# upload na drive
# extrakcija teksta
# cuvanje submissije
# cuvanje feedback-a # TODO - Dodati neki flag da nije finalni? (ili kod submissiona)
# NEMA cuvanje snapshot-a, to se tek radi nakon sto asistent potvrdi sve


@router.post(
    "/{chapter_name}/evaluative", response_model=GenericResponse
)  # problem, teorijske osnove, resenje, rezultati
def upload_chapter_evaluative(
    chapter_name: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
    llm=Depends(initialise_llm),
    drive_service=Depends(get_drive_service),
    upload_pdf_to_drive=Depends(get_upload_pdf),
    extract_pdf_to_markdown=Depends(get_extract_pdf_to_markdown),
    extract_chapter_text=Depends(get_extract_chapter_text),
    save_submission=Depends(get_save_submission),
    request_evaluation=Depends(get_request_evaluation),
    create_feedback_objects_for_evaluative_mode=Depends(
        get_create_feedback_objects_for_evaluative_mode
    ),
    file: UploadFile = File(...),
):
    file_bytes = anyio.run(file.read)
    # file_id, file_link = upload_pdf_to_drive(
    #    drive_service, file_bytes, current_user, chapter_name, "evalucioni"
    # )
    file_id = "random_id"
    file_link = "random_link"
    markdown_text = extract_pdf_to_markdown(file_bytes)
    extracted_text = extract_chapter_text(markdown_text, chapter_name, db)
    submission: Submission = save_submission(
        db,
        file_id,
        file_link,
        extracted_text,
        chapter_name,
        "Evalucioni mod",
        current_user.id,
    )
    llm_evaluation_response: LLMEvaluationResponse = request_evaluation(
        db, llm, submission, current_user, chapter_name
    )

    evaluations = create_feedback_objects_for_evaluative_mode(
        db, llm_evaluation_response.evaluation, chapter_name, submission
    )

    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message=f"Chapter '{chapter_name}' processed successfully.",
            data=evaluations,
        ).model_dump(),
    )


@router.get("/", response_model=GenericResponse)
def retrieve_chapters(
    db: Session = Depends(get_db),
    retrieve_chapters=Depends(get_retrieve_chapters),
):
    chapters: List[ChapterResponse] = retrieve_chapters(db)
    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message="Successfully retrieved chapters", data=chapters
        ).model_dump(),
    )
