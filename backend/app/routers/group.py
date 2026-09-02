import json
from typing import Annotated

from fastapi import APIRouter, Body, Depends, File, UploadFile, status
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session

from ..dependencies.auth import get_current_active_user, require_role
from ..dependencies.db import get_db
from ..models.role import Role
from ..models.user import User
from ..schemas.group import (
    CourseGroupsResponse,
    GroupCreate,
    GroupDetailResponse,
    GroupResponse,
    GroupUpdate,
)
from ..schemas.response import GenericResponse, IdResponse
from ..services.group import (
    create_group,
    get_group_detail,
    get_groups_for_instructor,
    get_students_in_group,
    import_students_into_group,
    modify_group,
    move_student_to_group,
    remove_group,
    remove_student_from_group,
    retrieve_active_groups,
)

router = APIRouter(
    prefix="/groups",
    tags=["groups"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_group_endpoint(
    group: Annotated[
        GroupCreate,
        Body(
            examples=[
                {
                    "name": "G_1_2025",
                    "short_name": "G1-2025",
                    "valid_from": "2025-01-01T00:00:00",
                    "valid_until": "2025-12-31T23:59:59",
                    "course_id": 1,
                    "student_ids": [10, 11, 12],
                }
            ]
        ),
    ],
    role: Annotated[Role, Depends(require_role("Instructor"))],
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    group_id = create_group(group, db, current_user.id)
    return JSONResponse(
        status_code=201,
        content=GenericResponse(
            message="Successfully created a new group.",
            data=IdResponse(id=group_id).model_dump(),
        ).model_dump(),
    )


@router.get("/", response_model=GenericResponse)
def retrieve_active_groups_endpoint(
    db: Session = Depends(get_db),
) -> GenericResponse:
    active_groups: list[GroupResponse] = retrieve_active_groups(db)
    return JSONResponse(
        status_code=200,
        content=json.loads(
            GenericResponse(
                message="Successfully retrieved active groups", data=active_groups
            ).model_dump_json()
        ),
    )


@router.get("/instructor", response_model=GenericResponse)
def retrieve_groups_for_instructor_endpoint(
    role: Annotated[Role, Depends(require_role("Instructor"))],
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    courses_with_groups = get_groups_for_instructor(db, current_user.id)
    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message="Successfully retrieved groups.",
            data=[
                CourseGroupsResponse.model_validate(c).model_dump(mode="json")
                for c in courses_with_groups
            ],
        ).model_dump(),
    )


@router.get("/{group_id}", response_model=GenericResponse)
def retrieve_group_detail_endpoint(
    group_id: int,
    role: Annotated[Role, Depends(require_role("Instructor"))],
    db: Session = Depends(get_db),
):
    detail = get_group_detail(db, group_id)
    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message="Student group retrieved successfully.",
            data=GroupDetailResponse.model_validate(detail).model_dump(mode="json"),
        ).model_dump(),
    )


@router.put("/{group_id}", status_code=204)
def update_group_endpoint(
    group_id: int,
    data: GroupUpdate,
    role: Annotated[Role, Depends(require_role("Instructor"))],
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    modify_group(db, group_id, data, current_user.id)
    return Response(status_code=204)


@router.delete("/{group_id}", status_code=204)
def delete_group_endpoint(
    group_id: int,
    role: Annotated[Role, Depends(require_role("Instructor"))],
    db: Session = Depends(get_db),
):
    remove_group(db, group_id)
    return Response(status_code=204)


@router.get("/{group_id}/students", response_model=GenericResponse)
def retrieve_students_in_group_endpoint(
    group_id: int,
    role: Annotated[Role, Depends(require_role("Instructor"))],
    db: Session = Depends(get_db),
):
    students = get_students_in_group(db, group_id)
    return JSONResponse(
        status_code=200,
        content=json.loads(
            GenericResponse(
                message="Successfully retrieved students.", data=students
            ).model_dump_json()
        ),
    )


@router.post("/{group_id}/students/batch", status_code=status.HTTP_201_CREATED)
def import_students_into_group_endpoint(
    group_id: int,
    role: Annotated[Role, Depends(require_role("Instructor"))],
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    imported = import_students_into_group(db, group_id, file)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=GenericResponse(
            message=f"Successfully imported {imported} students into the group.",
            data=None,
        ).model_dump(),
    )


@router.put("/{group_id}/students/{user_id}", response_model=GenericResponse)
def move_student_to_group_endpoint(
    group_id: int,
    user_id: int,
    role: Annotated[Role, Depends(require_role("Instructor"))],
    db: Session = Depends(get_db),
):
    move_student_to_group(db, group_id, user_id)
    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message="Successfully moved the student into the group.", data=None
        ).model_dump(),
    )


@router.delete("/{group_id}/students/{user_id}", response_model=GenericResponse)
def remove_student_from_group_endpoint(
    group_id: int,
    user_id: int,
    role: Annotated[Role, Depends(require_role("Instructor"))],
    db: Session = Depends(get_db),
):
    remove_student_from_group(db, group_id, user_id)
    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message="Successfully removed the student from the group.", data=None
        ).model_dump(),
    )
