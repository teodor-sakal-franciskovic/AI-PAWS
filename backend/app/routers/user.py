import json

from typing import Annotated

from fastapi import APIRouter, Body, Depends, File, UploadFile, status
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session

from ..dependencies.auth import (
    get_current_active_user,
    get_current_active_user_role,
    require_role,
)
from ..dependencies.db import get_db
from ..dependencies.user import (
    get_batch_users,
    get_create_user,
    get_deactivate_user,
    get_retrieve_logged_in_user,
    get_update_user_info,
    get_update_user_password,
    get_retrieve_submissions_for_specific_chapter,
    get_retrieve_evaluative_submissions_for_ta_students,
    get_grade_submission,
)
from ..models.role import Role
from ..models.user import User
from ..schemas.submission import SubmissionResponse, TAEvaluationGradesRequest
from ..schemas.response import GenericResponse
from ..schemas.user import (
    UpdatedUserInfo,
    UpdatedUserPassword,
    UserCreate,
    UserResponse,
    EvaluativeUserSubmissionResponse,
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
                    "role_id": 1,
                }
            ]
        ),
    ],
    db: Session = Depends(get_db),
    create_user=Depends(get_create_user),
) -> GenericResponse:
    created_user: UserResponse = create_user(user, db)
    return JSONResponse(
        status_code=201,
        content=GenericResponse(
            message="Successfully created user", data=created_user
        ).model_dump(),
    )


@router.get("/me", tags=["users"], response_model=GenericResponse)
def retrieve_logged_in_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
    role: Annotated[Role, Depends(get_current_active_user_role)],
    retrieve_logged_in_user=Depends(get_retrieve_logged_in_user),
) -> GenericResponse:
    logged_in_user: UserResponse = retrieve_logged_in_user(current_user, role)
    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message="Successfully retrieved the logged-in user", data=logged_in_user
        ).model_dump(),
    )


@router.put("/info", tags=["users"], response_model=GenericResponse)
def update_user_info(
    updated_user_info: Annotated[
        UpdatedUserInfo,
        Body(examples=[{"name": "Peter", "surname": "Hecox!"}]),
    ],
    current_user: Annotated[User, Depends(get_current_active_user)],
    role: Annotated[Role, Depends(get_current_active_user_role)],
    db: Session = Depends(get_db),
    update_user_info=Depends(get_update_user_info),
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
def update_user_password(
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
    update_user_password=Depends(get_update_user_password),
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
def deactivate_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
    deactivate_user=Depends(get_deactivate_user),
):
    deactivate_user(current_user, db)
    return Response(
        status_code=204,
    )


@router.post("/batch", tags=["users"], status_code=status.HTTP_201_CREATED)
def create_users_batch(
    role: Annotated[Role, Depends(require_role("TA"))],
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    batch_users=Depends(get_batch_users),
):
    batch_users(file, db)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=GenericResponse(
            message="Succesfully imported users from the provided file.", data=None
        ).model_dump(),
    )


@router.get("/chapter/{chapter_id}/submissions")
def retrieve_submissions_for_chapter(
    chapter_id: int,
    role: Annotated[Role, Depends(require_role("Student"))],
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
    retrieve_submissions_for_specific_chapter=Depends(
        get_retrieve_submissions_for_specific_chapter
    ),
):
    submissions: list[SubmissionResponse] = retrieve_submissions_for_specific_chapter(
        db, current_user, chapter_id
    )
    return JSONResponse(
        status_code=200,
        content=json.loads(
            GenericResponse(
                message=f"Succesfully retrieved submissions for user {current_user.id}, for chapter {chapter_id}.",
                data=submissions,
            ).model_dump_json()
        ),
    )


@router.get("/my-students/submissions/evaluative")
def retrieve_my_students_evaluative_submissions(
    role: Annotated[Role, Depends(require_role("TA"))],
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
    retrieve_evaluative_submissions_for_ta_students=Depends(
        get_retrieve_evaluative_submissions_for_ta_students
    ),
):
    evaluative_submissions: EvaluativeUserSubmissionResponse = (
        retrieve_evaluative_submissions_for_ta_students(db, current_user)
    )
    return JSONResponse(
        status_code=200,
        content=json.loads(
            GenericResponse(
                message="Successfully retrieved evaluative submissions",
                data=evaluative_submissions,
            ).model_dump_json(),
        ),
    )


@router.put("/submission/{submission_id}/grade")
def grade_submission(
    submission_id: int,
    body: TAEvaluationGradesRequest,
    role: Annotated[Role, Depends(require_role("TA"))],
    db: Session = Depends(get_db),
    grade_submission=Depends(get_grade_submission),
):
    grade_submission(db, submission_id, body)
    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message=f"Successfully graded submission for submission {submission_id}",
            data=None,
        ).model_dump(),
    )
