import json
from typing import Annotated
from copy import deepcopy

from fastapi import (
    APIRouter,
    Body,
    Depends,
    File,
    UploadFile,
    status,
    BackgroundTasks,
)
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session

from ..dependencies.auth import (
    get_current_active_user,
    get_current_active_user_role,
    require_role,
)
from ..dependencies.db import get_db
from ..dependencies.llm import initialise_llm

from ..services.user import (
    batch_users,
    create_user,
    deactivate_user,
    retrieve_logged_in_user,
    update_user_info,
    update_user_password,
    retrieve_evaluative_submissions_for_ta_students,
    grade_submission,
    retrieve_user_by_id,
    read_pretest_results,
)
from ..services.submission import retrieve_submission
from ..services.historical_profile import (
    insert_historical_profile_snapshot,
    retrieve_updated_student_knowledge_from_evaluative_mode,
)

from ..tasks.user import generate_initial_student_knowledge

from ..llm.schema import LLMUpdatedKnowledge
from ..models.role import Role
from ..models.user import User
from ..models.submission import Submission
from ..schemas.submission import TAEvaluationGradesRequest
from ..schemas.response import GenericResponse
from ..schemas.user import (
    UpdatedUserInfo,
    UpdatedUserPassword,
    UserCreate,
    UserResponse,
    EvaluativeUsersSubmissionResponse,
)

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.post("/registration", tags=["users"], response_model=GenericResponse)
def register(
    user: Annotated[
        UserCreate,
        Body(
            examples=[
                {
                    "email": "example@email.com",
                    "password": "Example123!",
                    "name": "John",
                    "surname": "Padilla",
                    "role_id": 2,
                }
            ]
        ),
    ],
    db: Session = Depends(get_db),
) -> GenericResponse:
    created_user: UserResponse = create_user(user, db)
    return JSONResponse(
        status_code=201,
        content=GenericResponse(
            message="Successfully created user", data=created_user
        ).model_dump(),
    )


@router.get("/me", tags=["users"], response_model=GenericResponse)
def retrieve_logged_in_user_endpoint(
    current_user: Annotated[User, Depends(get_current_active_user)],
    role: Annotated[Role, Depends(get_current_active_user_role)],
) -> GenericResponse:
    logged_in_user: UserResponse = retrieve_logged_in_user(current_user, role)
    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message="Successfully retrieved the logged-in user", data=logged_in_user
        ).model_dump(),
    )


@router.put("/info", tags=["users"], response_model=GenericResponse)
def update_user_info_endpoint(
    updated_user_info: Annotated[
        UpdatedUserInfo, Body(examples=[{"name": "Peter", "surname": "Hecox!"}])
    ],
    current_user: Annotated[User, Depends(get_current_active_user)],
    role: Annotated[Role, Depends(get_current_active_user_role)],
    db: Session = Depends(get_db),
) -> GenericResponse:
    updated_user: UserResponse = update_user_info(
        current_user, updated_user_info, role, db
    )
    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message="Succesfully updated user info", data=updated_user
        ).model_dump(),
    )


@router.put("/password", tags=["users"], response_model=GenericResponse)
def update_user_password_endpoint(
    updated_password: Annotated[
        UpdatedUserPassword,
        Body(
            examples=[
                {"password": "NewPassword123!", "confirmed_password": "NewPassword123!"}
            ]
        ),
    ],
    current_user: Annotated[User, Depends(get_current_active_user)],
    role: Annotated[Role, Depends(get_current_active_user_role)],
    db: Session = Depends(get_db),
):
    updated_user: UserResponse = update_user_password(
        current_user, updated_password, role, db
    )
    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message="Succesfully updated user password", data=updated_user
        ).model_dump(),
    )


@router.delete("/", tags=["users"], status_code=204)
def deactivate_user_endpoint(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    deactivate_user(current_user, db)
    return Response(status_code=204)


@router.post("/batch", tags=["users"], status_code=status.HTTP_201_CREATED)
def create_users_batch(
    role: Annotated[Role, Depends(require_role("Instructor"))],
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    batch_users(file, db)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=GenericResponse(
            message="Succesfully imported users from the provided file.", data=None
        ).model_dump(),
    )


@router.get("/my-students/submissions/evaluative")
def retrieve_my_students_evaluative_submissions(
    role: Annotated[Role, Depends(require_role("Instructor"))],
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    evaluative_submissions: EvaluativeUsersSubmissionResponse = (
        retrieve_evaluative_submissions_for_ta_students(db, current_user)
    )
    return JSONResponse(
        status_code=200,
        content=json.loads(
            GenericResponse(
                message="Successfully retrieved evaluative submissions",
                data=evaluative_submissions,
            ).model_dump_json()
        ),
    )


@router.put("/submission/{submission_id}/grade")
def grade_submission_endpoint(
    submission_id: int,
    body: TAEvaluationGradesRequest,
    role: Annotated[Role, Depends(require_role("Instructor"))],
    llm=Depends(initialise_llm),
    db: Session = Depends(get_db),
):
    submission: Submission = retrieve_submission(db, submission_id)
    initial_graded_status = deepcopy(submission.graded)
    grade_submission(db, submission_id, body)
    if not initial_graded_status:
        updated_student_knowledge: LLMUpdatedKnowledge = (
            retrieve_updated_student_knowledge_from_evaluative_mode(
                db, llm, body, submission_id
            )
        )
        user: User = retrieve_user_by_id(db, submission.user_id)
        insert_historical_profile_snapshot(
            db, user, submission, updated_student_knowledge.updated_knowledge
        )
    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message=f"Successfully graded submission for submission {submission_id}",
            data=None,
        ).model_dump(),
    )


@router.post("/initial-knowledge", tags=["users"], status_code=status.HTTP_201_CREATED)
def create_students_initial_knowledge(
    background_tasks: BackgroundTasks,
    role: Annotated[Role, Depends(require_role("Instructor"))],
    llm=Depends(initialise_llm),
    file: UploadFile = File(...),
):
    df = read_pretest_results(file)

    background_tasks.add_task(generate_initial_student_knowledge, df, llm)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=GenericResponse(
            message=f"Succesfully uploaded pretest results. Generating the initial knowledge for {df['Indeks'].nunique()} students in the background...",
            data=None,
        ).model_dump(),
    )
