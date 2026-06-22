import json
import anyio

from typing import Annotated
from fastapi import APIRouter, Depends, File, UploadFile, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..dependencies.auth import get_current_active_user, require_role
from ..dependencies.db import get_db
from ..dependencies.llm import initialise_llm

from ..services.assignment import (
    create_assignment,
    retrieve_active_assignments_for_student,
    retrieve_previous_assignments_for_student,
    retrieve_submission_files_for_assignment,
    retrieve_assignments,
)
from ..services.chapter import extract_pdf_to_markdown, retrieve_chapter_object_by_id
from ..services.submission import save_submission

from ..tasks.assignment import retrieve_llm_grading, retrieve_llm_feedback

from ..models.submission import Submission, SubmissionStatus
from ..models.user import User
from ..models.role import Role
from ..models.chapter import Chapter

from ..schemas.response import GenericResponse
from ..schemas.assignment import (
    AssignmentCreate,
    AssignmentResponse,
    SubmittedSubmissionForAssignmentResponse,
)


router = APIRouter(
    prefix="/assignments",
    tags=["assignments"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=GenericResponse)
def create_assignment_endpoint(
    body: AssignmentCreate,
    role: Annotated[Role, Depends(require_role("TA"))],
    db: Session = Depends(get_db),
):
    assignment_response: AssignmentResponse = create_assignment(db, body)
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
def retrieve_active_assignments_endpoint(
    current_user: Annotated[User, Depends(get_current_active_user)],
    role: Annotated[Role, Depends(require_role("Student"))],
    db: Session = Depends(get_db),
):
    active_assignments: list[SubmittedSubmissionForAssignmentResponse] = (
        retrieve_active_assignments_for_student(db, current_user)
    )
    return JSONResponse(
        status_code=200,
        content=json.loads(
            GenericResponse(
                message=f"Retrieved active assignments for student {current_user.email} successfully.",
                data=active_assignments,
            ).model_dump_json()
        ),
    )


@router.get("/previous", response_model=GenericResponse)
def retrieve_previous_assignments_endpoint(
    role: Annotated[Role, Depends(require_role("Student"))],
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    finished_assignments: list[SubmittedSubmissionForAssignmentResponse] = (
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


@router.get("/")
def retrieve_all_assignments_endpoint(
    role: Annotated[Role, Depends(require_role("TA"))],
    db: Session = Depends(get_db),
):
    assignments_response: list[AssignmentResponse] = retrieve_assignments(db)
    return JSONResponse(
        status_code=200,
        content=json.loads(
            GenericResponse(
                message="Retrieved all assignments successfully.",
                data=assignments_response,
            ).model_dump_json()
        ),
    )


@router.get("/{assignment_id}/submissions/files")
def retrieve_submission_files_endpoint(
    assignment_id: int,
    role: Annotated[Role, Depends(require_role("TA"))],
    db: Session = Depends(get_db),
):
    return retrieve_submission_files_for_assignment(db, assignment_id)


@router.post(
    "/{assignment_id}/chapters/{chapter_id}/interactive",
    response_model=GenericResponse,
)
def upload_chapter_interactive(
    assignment_id: int,
    chapter_id: int,
    background_tasks: BackgroundTasks,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
    llm=Depends(initialise_llm),
    file: UploadFile = File(...),
):
    chapter: Chapter = retrieve_chapter_object_by_id(db, chapter_id)
    chapter_name: str = chapter.name.lower()
    file_bytes = anyio.run(file.read)
    markdown_text = extract_pdf_to_markdown(file_bytes)
    submission: Submission = save_submission(
        db,
        markdown_text,
        chapter_name,
        "Interactive mode",
        current_user.id,
        assignment_id,
        file_bytes,
        SubmissionStatus.PENDING,
    )

    background_tasks.add_task(
        retrieve_llm_feedback, submission.id, current_user.id, chapter_name, llm
    )

    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message=f"Chapter '{chapter_name}' uploaded successfully.",
            data={"submission_id": submission.id},
        ).model_dump(),
    )


@router.post(
    "/{assignment_id}/chapters/{chapter_id}/evaluative",
    response_model=GenericResponse,
)
def upload_chapter_evaluative(
    assignment_id: int,
    chapter_id: int,
    background_tasks: BackgroundTasks,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
    llm=Depends(initialise_llm),
    file: UploadFile = File(...),
):
    chapter: Chapter = retrieve_chapter_object_by_id(db, chapter_id)
    chapter_name: str = chapter.name.lower()
    file_bytes = anyio.run(file.read)
    markdown_text = extract_pdf_to_markdown(file_bytes)

    submission: Submission = save_submission(
        db,
        markdown_text,
        chapter_name,
        "Evaluative mode",
        current_user.id,
        assignment_id,
        file_bytes,
        SubmissionStatus.PENDING,
    )

    background_tasks.add_task(
        retrieve_llm_grading, submission.id, current_user.id, chapter_name, llm
    )

    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message=f"Chapter '{chapter_name}' uploaded successfully.",
            data={"submission_id": submission.id},
        ).model_dump(),
    )
