import json
import anyio

from typing import Annotated
from fastapi import APIRouter, Depends, File, UploadFile, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..dependencies.assignment import (
    get_create_assignment,
    get_retrieve_active_assignments_for_student,
    get_retrieve_previous_assignments_for_student,
    get_retrieve_submission_files_for_assignment,
    get_retrieve_assignments,
)
from ..dependencies.auth import get_current_active_user, require_role
from ..dependencies.chapter import (
    get_extract_pdf_to_markdown,
    get_retrieve_chapter_object_by_id,
)
from ..dependencies.db import get_db, get_new_session
from ..dependencies.feedback import (
    get_request_initial_interactive_feedback,
    get_create_feedback_objects_for_interactive_mode,
    get_request_evaluation,
    get_create_feedback_objects_for_evaluative_mode,
)
from ..dependencies.llm import initialise_llm
from ..dependencies.submission import get_save_submission
from ..dependencies.historical_profile import get_insert_historical_profile_snapshot
from ..dependencies.submission import get_update_submission_status


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

from ..llm.schema import LLMFeedbackResponse, LLMEvaluationResponse
from ..utils.logger import logger


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
def retrieve_previous_assignments(
    role: Annotated[Role, Depends(require_role("Student"))],
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
    retrieve_previous_assignments_for_student=Depends(
        get_retrieve_previous_assignments_for_student
    ),
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
def retrieve_all_assignments(
    role: Annotated[Role, Depends(require_role("TA"))],
    db: Session = Depends(get_db),
    retrieve_assignments=Depends(get_retrieve_assignments),
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
def retrieve_submission_files(
    assignment_id: int,
    role: Annotated[Role, Depends(require_role("TA"))],
    db: Session = Depends(get_db),
    retrieve_submission_files_for_assignment=Depends(
        get_retrieve_submission_files_for_assignment
    ),
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
    extract_pdf_to_markdown=Depends(get_extract_pdf_to_markdown),
    save_submission=Depends(get_save_submission),
    request_initial_interactive_feedback=Depends(
        get_request_initial_interactive_feedback
    ),
    create_feedback_objects_for_interactive_mode=Depends(
        get_create_feedback_objects_for_interactive_mode
    ),
    insert_historical_profile_snapshot=Depends(get_insert_historical_profile_snapshot),
    retrieve_chapter_by_id=Depends(get_retrieve_chapter_object_by_id),
    update_submission_status=Depends(get_update_submission_status),
    file: UploadFile = File(...),
):
    chapter: Chapter = retrieve_chapter_by_id(db, chapter_id)
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

    def retrieve_llm_feedback(submission_id: int, user_id: int, chapter_name: str):
        logger.info("[BACKGROUND] Starting a background DB session...")
        db = get_new_session()
        try:
            logger.info(f"[BACKGROUND] Retrieving submission {submission_id}")
            submission = db.get(Submission, submission_id)
            logger.info(
                f"[BACKGROUND] Successfully retrieved submission {submission_id}"
            )

            logger.info(f"[BACKGROUND] Retrieving user {user_id}...")
            user = db.get(User, user_id)
            logger.info(f"[BACKGROUND] Successfully retrieved user {user_id}")

            logger.info("[BACKGROUND] Requesting LLM feedback...")
            llm_feedback_response: LLMFeedbackResponse = (
                request_initial_interactive_feedback(
                    db, llm, submission, user, chapter_name
                )
            )

            logger.info("[BACKGROUND] Creating interactive feedback object...")
            create_feedback_objects_for_interactive_mode(
                db, llm_feedback_response.feedback, chapter_name, submission
            )

            logger.info("[BACKGROUND] Inserting historical profile...")
            insert_historical_profile_snapshot(
                db, user, submission, llm_feedback_response.updated_knowledge
            )

            logger.info("[BACKGROUND] Updating submission status to COMPLETED...")
            update_submission_status(db, submission, SubmissionStatus.COMPLETED)
            logger.info(
                "[BACKGROUND] Successfully updated submission status to COMPLETED"
            )
            db.commit()
        except Exception as e:
            logger.info(f"[BACKGROUND] An error occurred: {e}")
            db.rollback()
            logger.info("[BACKGROUND] Updating submission status to FAILED...")
            update_submission_status(db, submission, SubmissionStatus.FAILED)
            logger.info("[BACKGROUND] Successfully updated submission status to FAILED")
            db.commit()
        finally:
            db.close()

    background_tasks.add_task(
        retrieve_llm_feedback, submission.id, current_user.id, chapter_name
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
    extract_pdf_to_markdown=Depends(get_extract_pdf_to_markdown),
    save_submission=Depends(get_save_submission),
    request_evaluation=Depends(get_request_evaluation),
    create_feedback_objects_for_evaluative_mode=Depends(
        get_create_feedback_objects_for_evaluative_mode
    ),
    retrieve_chapter_by_id=Depends(get_retrieve_chapter_object_by_id),
    update_submission_status=Depends(get_update_submission_status),
    file: UploadFile = File(...),
):
    chapter: Chapter = retrieve_chapter_by_id(db, chapter_id)
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

    def retrieve_llm_grading(submission_id: int, user_id: int, chapter_name: str):
        logger.info("[BACKGROUND] Starting a background DB session...")
        db = get_new_session()
        try:
            logger.info(f"[BACKGROUND] Retrieving submission {submission_id}")
            submission = db.get(Submission, submission_id)
            logger.info(
                f"[BACKGROUND] Successfully retrieved submission {submission_id}"
            )

            logger.info(f"[BACKGROUND] Retrieving user {user_id}...")
            user = db.get(User, user_id)
            logger.info(f"[BACKGROUND] Successfully retrieved user {user_id}")

            logger.info("[BACKGROUND] Requesting LLM evaluation...")
            llm_evaluation_response: LLMEvaluationResponse = request_evaluation(
                db, llm, submission, user, chapter_name
            )

            logger.info("[BACKGROUND] Creating feedback objects...")
            create_feedback_objects_for_evaluative_mode(
                db, llm_evaluation_response.evaluation, chapter_name, submission
            )

            logger.info("[BACKGROUND] Updating submission status to COMPLETED...")
            update_submission_status(db, submission, SubmissionStatus.COMPLETED)
            logger.info(
                "[BACKGROUND] Successfully updated submission status to COMPLETED"
            )
            db.commit()
        except Exception as e:
            logger.info(f"[BACKGROUND] An error occurred: {e}")
            db.rollback()
            logger.info("[BACKGROUND] Updating submission status to FAILED...")
            update_submission_status(db, submission, SubmissionStatus.FAILED)
            logger.info("[BACKGROUND] Successfully updated submission status to FAILED")
            db.commit()
        finally:
            db.close()

    background_tasks.add_task(
        retrieve_llm_grading, submission.id, current_user.id, chapter_name
    )

    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message=f"Chapter '{chapter_name}' uploaded successfully.",
            data={"submission_id": submission.id},
        ).model_dump(),
    )
