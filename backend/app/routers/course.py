from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..dependencies.auth import get_current_active_user, require_role
from ..dependencies.db import get_db
from ..models.role import Role
from ..models.user import User
from ..schemas.course import (
    CourseCreate,
    CourseDetailResponse,
    CourseResponse,
    CourseUpdate,
)
from ..schemas.response import GenericResponse
from ..services.course import (
    create_course,
    get_courses_for_instructor,
    get_courses_for_student,
    update_course,
)
from ..tasks.course import generate_prompt_descriptions

router = APIRouter(
    prefix="/courses",
    tags=["courses"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=GenericResponse)
def create_course_endpoint(
    data: CourseCreate,
    background_tasks: BackgroundTasks,
    role: Annotated[Role, Depends(require_role("Instructor"))],
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    course = create_course(db, data, current_user.id)
    background_tasks.add_task(generate_prompt_descriptions, course.id)
    return JSONResponse(
        status_code=201,
        content=GenericResponse(
            message="Course successfully created. Prompt descriptions are being generated in the background.",
            data=CourseResponse.model_validate(course).model_dump(mode="json"),
        ).model_dump(),
    )


@router.get("/instructor", response_model=GenericResponse)
def get_courses_endpoint(
    role: Annotated[Role, Depends(require_role("Instructor"))],
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    courses = get_courses_for_instructor(db, current_user.id)
    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message="Successfully retrieved courses.",
            data=[
                CourseDetailResponse.model_validate(c).model_dump(mode="json")
                for c in courses
            ],
        ).model_dump(),
    )


@router.get("/student", response_model=GenericResponse)
def get_courses_for_student_endpoint(
    role: Annotated[Role, Depends(require_role("Student"))],
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    if not current_user.group_id:
        return JSONResponse(
            status_code=200,
            content=GenericResponse(message="No courses found.", data=[]).model_dump(),
        )
    courses = get_courses_for_student(db, current_user.group_id)
    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message="Successfully retrieved courses.",
            data=[
                CourseDetailResponse.model_validate(c).model_dump(mode="json")
                for c in courses
            ],
        ).model_dump(),
    )


@router.put("/{course_id}", response_model=GenericResponse)
def update_course_endpoint(
    course_id: int,
    data: CourseUpdate,
    background_tasks: BackgroundTasks,
    role: Annotated[Role, Depends(require_role("Instructor"))],
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    course, rule_ids = update_course(db, course_id, data, current_user.id)
    if rule_ids:
        background_tasks.add_task(generate_prompt_descriptions, course.id)
    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message="Course successfully updated.",
            data=CourseResponse.model_validate(course).model_dump(mode="json"),
        ).model_dump(),
    )
