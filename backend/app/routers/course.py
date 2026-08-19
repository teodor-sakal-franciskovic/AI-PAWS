from typing import Annotated, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..dependencies.auth import get_current_active_user, require_role
from ..dependencies.db import get_db
from ..models.role import Role
from ..models.user import User
from ..schemas.course import (
    CourseCreate,
    CourseDetailResponse,
    CourseNameCheckResponse,
    CourseResponse,
    CourseUpdate,
    CourseWithTakenNamesResponse,
)
from ..schemas.response import GenericResponse
from ..services.course import (
    check_course_name,
    create_course,
    get_all_courses,
    get_course_by_id,
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


@router.get("/", response_model=GenericResponse)
def get_all_courses_endpoint(
    role: Annotated[Role, Depends(require_role("Instructor"))],
    db: Session = Depends(get_db),
):
    courses = get_all_courses(db)
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


@router.get("/name/{name}", response_model=GenericResponse)
def check_course_name_endpoint(
    name: str,
    role: Annotated[Role, Depends(require_role("Instructor"))],
    exclude_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    used = check_course_name(db, name, exclude_id)
    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message="Successfully checked course name availability.",
            data=CourseNameCheckResponse(course_name_used=used).model_dump(),
        ).model_dump(),
    )


@router.get("/{course_id}", response_model=GenericResponse)
def get_course_by_id_endpoint(
    course_id: int,
    role: Annotated[Role, Depends(require_role("Instructor"))],
    db: Session = Depends(get_db),
):
    course = get_course_by_id(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message="Successfully retrieved course.",
            data=CourseWithTakenNamesResponse.model_validate(course).model_dump(
                mode="json"
            ),
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
