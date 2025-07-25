import json
import anyio

from typing import Annotated
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..dependencies.assignment import (
    get_create_assignment,
    get_retrieve_active_assignments_for_student,
    get_retrieve_previous_assignments_for_student,
)
from ..dependencies.auth import get_current_active_user, require_role
from ..dependencies.chapter import (
    get_extract_chapter_text,
    get_extract_pdf_to_markdown,
    get_retrieve_chapter_object_by_id,
)
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

from ..models.submission import Submission
from ..models.user import User
from ..models.role import Role
from ..models.chapter import Chapter

from ..schemas.response import GenericResponse
from ..schemas.feedback import InteractiveFeedbackResponse
from ..schemas.assignment import (
    AssignmentCreate,
    AssignmentResponse,
    FinishedAssignmentResponse,
)

from ..llm.schema import LLMFeedbackResponse, LLMEvaluationResponse


router = APIRouter(
    prefix="/assignments",
    tags=["assignments"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=GenericResponse)
def create_assignment(
    body: AssignmentCreate,
    role: Annotated[Role, Depends(require_role("TA"))],
    db: Session = Depends(get_db),
    create_assignment_object=Depends(get_create_assignment),
):
    assignment_response: AssignmentResponse = create_assignment_object(db, body)
    return JSONResponse(
        status_code=200,
        content=json.loads(
            GenericResponse(
                message=f"Assignment {assignment_response.name} created successfully.",
                data=assignment_response,
            ).model_dump_json()
        ),
    )


@router.get("/active", response_model=GenericResponse)
def retrieve_active_assignments(
    current_user: Annotated[User, Depends(get_current_active_user)],
    role: Annotated[Role, Depends(require_role("Student"))],
    db: Session = Depends(get_db),
    retrieve_active_assignments_for_student=Depends(
        get_retrieve_active_assignments_for_student
    ),
):
    assignments: list[AssignmentResponse] = retrieve_active_assignments_for_student(
        db, current_user
    )
    return JSONResponse(
        status_code=200,
        content=json.loads(
            GenericResponse(
                message=f"Retrieved active assignments for student {current_user.email} successfully.",
                data=assignments,
            ).model_dump_json()
        ),
    )


@router.get("/previous", response_model=GenericResponse)
def retrieve_previous_assignments(
    role: Annotated[Role, Depends(require_role("Student"))],
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
    retrieve_previous_assignments_for_student=Depends(
        get_retrieve_previous_assignments_for_student
    ),
):
    finished_assignments: list[FinishedAssignmentResponse] = (
        retrieve_previous_assignments_for_student(db, current_user)
    )
    return JSONResponse(
        status_code=200,
        content=json.loads(
            GenericResponse(
                message=f"Succesfully retrieved previous assignments with submissions for user {current_user.id}.",
                data=finished_assignments,
            ).model_dump_json()
        ),
    )


@router.post(
    "/{assignment_id}/chapters/{chapter_id}/interactive",
    response_model=GenericResponse,
)
def upload_chapter_interactive(
    assignment_id: int,
    chapter_id: int,
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
    retrieve_chapter_by_id=Depends(get_retrieve_chapter_object_by_id),
    file: UploadFile = File(...),
):
    chapter: Chapter = retrieve_chapter_by_id(db, chapter_id)
    chapter_name: str = chapter.name.lower()
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
        assignment_id,
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


@router.post(
    "/{assignment_id}/chapters/{chapter_id}/evaluative",
    response_model=GenericResponse,
)
def upload_chapter_evaluative(
    assignment_id: int,
    chapter_id: int,
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
    retrieve_chapter_by_id=Depends(get_retrieve_chapter_object_by_id),
    file: UploadFile = File(...),
):
    chapter: Chapter = retrieve_chapter_by_id(db, chapter_id)
    chapter_name: str = chapter.name.lower()
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
        assignment_id,
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
