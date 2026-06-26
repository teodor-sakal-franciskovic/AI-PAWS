from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..dependencies.auth import require_role
from ..dependencies.db import get_db
from ..models.role import Role
from ..schemas.course import CourseCreate, CourseResponse
from ..schemas.response import GenericResponse
from ..services.course import create_course
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
    role: Annotated[Role, Depends(require_role("TA"))],
    db: Session = Depends(get_db),
):
    course = create_course(db, data)
    background_tasks.add_task(generate_prompt_descriptions, course.id)
    return JSONResponse(
        status_code=201,
        content=GenericResponse(
            message="Course successfully created. Prompt descriptions are being generated in the background.",
            data=CourseResponse.model_validate(course).model_dump(mode="json"),
        ).model_dump(),
    )
