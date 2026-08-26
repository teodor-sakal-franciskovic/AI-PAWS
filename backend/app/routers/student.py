from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..dependencies.auth import require_role
from ..dependencies.db import get_db
from ..models.role import Role
from ..schemas.response import GenericResponse
from ..services.student import register_students, search_students_service

router = APIRouter(
    prefix="/students",
    tags=["students"],
    responses={404: {"description": "Not found"}},
)


@router.post("/batch", status_code=status.HTTP_201_CREATED)
def register_students_endpoint(
    role: Annotated[Role, Depends(require_role("Instructor"))],
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    registered = register_students(file, db)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=GenericResponse(
            message=f"Successfully registered {registered} students.",
            data=None,
        ).model_dump(),
    )


@router.get("/search", response_model=GenericResponse)
def search_students_endpoint(
    role: Annotated[Role, Depends(require_role("Instructor"))],
    email: str | None = None,
    name: str | None = None,
    surname: str | None = None,
    faculty: str | None = None,
    index: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db),
):
    result = search_students_service(
        db, email, name, surname, faculty, index, page, page_size
    )
    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message="Successfully searched students.",
            data=result.model_dump(mode="json"),
        ).model_dump(),
    )
