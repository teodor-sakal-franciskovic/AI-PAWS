from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session

from ..dependencies.auth import get_current_active_user, require_role
from ..dependencies.db import get_db
from ..exceptions import ApiError
from ..models.role import Role
from ..models.user import User
from ..schemas.course import CourseCreate, CourseDetailResponse, CourseUpdate
from ..schemas.group import StudentIdsRequest
from ..schemas.response import GenericResponse, IdResponse, NameAvailabilityResponse
from ..services.course import (
    create_course,
    delete_course,
    get_all_courses,
    get_course_by_id,
    get_courses_for_instructor,
    get_courses_for_student,
    is_course_name_available,
    update_course,
)
from ..services.group import (
    assign_students_to_instructor_for_course,
    get_assigned_students_for_instructor,
    get_unassigned_students_for_course,
    unassign_students_from_instructor_for_course,
)

router = APIRouter(
    prefix="/courses",
    tags=["courses"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=GenericResponse, status_code=201)
def create_course_endpoint(
    data: CourseCreate,
    role: Annotated[Role, Depends(require_role("Instructor"))],
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    course_id = create_course(db, data, current_user.id)
    return JSONResponse(
        status_code=201,
        content=GenericResponse(
            message="Course successfully created.",
            data=IdResponse(id=course_id).model_dump(),
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
    courses = get_courses_for_student(db, current_user.id)
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


@router.get("/check-name", response_model=GenericResponse)
def check_course_name_endpoint(
    role: Annotated[Role, Depends(require_role("Instructor"))],
    name: str,
    exclude_id: int | None = None,
    db: Session = Depends(get_db),
):
    available = is_course_name_available(db, name, exclude_id)
    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message="Successfully checked course name availability.",
            data=NameAvailabilityResponse(name_available=available).model_dump(),
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
        raise ApiError(404, "COURSE_NOT_FOUND", "Course not found.")
    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message="Successfully retrieved course.",
            data=CourseDetailResponse.model_validate(course).model_dump(mode="json"),
        ).model_dump(),
    )


@router.put("/{course_id}", status_code=204)
def update_course_endpoint(
    course_id: int,
    data: CourseUpdate,
    role: Annotated[Role, Depends(require_role("Instructor"))],
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    update_course(db, course_id, data, current_user.id)
    return Response(status_code=204)


@router.delete("/{course_id}", status_code=204)
def delete_course_endpoint(
    course_id: int,
    role: Annotated[Role, Depends(require_role("Instructor"))],
    db: Session = Depends(get_db),
):
    delete_course(db, course_id)
    return Response(status_code=204)


@router.get("/{course_id}/students/mine", response_model=GenericResponse)
def get_my_students_for_course_endpoint(
    course_id: int,
    role: Annotated[Role, Depends(require_role("Instructor"))],
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    students = get_assigned_students_for_instructor(db, course_id, current_user.id)
    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message="Successfully retrieved your assigned students for this course.",
            data=[s.model_dump(mode="json") for s in students],
        ).model_dump(),
    )


@router.get("/{course_id}/students/unassigned", response_model=GenericResponse)
def get_unassigned_students_for_course_endpoint(
    course_id: int,
    role: Annotated[Role, Depends(require_role("Instructor"))],
    db: Session = Depends(get_db),
):
    students = get_unassigned_students_for_course(db, course_id)
    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message="Successfully retrieved unassigned students for this course.",
            data=[s.model_dump(mode="json") for s in students],
        ).model_dump(),
    )


@router.post("/{course_id}/students/assign", status_code=204)
def assign_students_for_course_endpoint(
    course_id: int,
    data: StudentIdsRequest,
    role: Annotated[Role, Depends(require_role("Instructor"))],
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    assign_students_to_instructor_for_course(
        db, course_id, data.student_ids, current_user.id
    )
    return Response(status_code=204)


@router.post("/{course_id}/students/unassign", status_code=204)
def unassign_students_for_course_endpoint(
    course_id: int,
    data: StudentIdsRequest,
    role: Annotated[Role, Depends(require_role("Instructor"))],
    db: Session = Depends(get_db),
):
    unassign_students_from_instructor_for_course(db, course_id, data.student_ids)
    return Response(status_code=204)
