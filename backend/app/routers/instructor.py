from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..dependencies.auth import require_role
from ..dependencies.db import get_db
from ..models.role import Role
from ..models.user import User
from ..schemas.response import GenericResponse
from ..schemas.user import UserSummaryResponse
from ..services.user import retrieve_instructors

router = APIRouter(
    prefix="/instructors",
    tags=["instructors"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=GenericResponse)
def retrieve_instructors_endpoint(
    role: Annotated[Role, Depends(require_role("Instructor"))],
    db: Session = Depends(get_db),
) -> GenericResponse:
    instructors: list[User] = retrieve_instructors(db)
    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message="Successfully retrieved instructors",
            data=[
                UserSummaryResponse.model_validate(instructor).model_dump(mode="json")
                for instructor in instructors
            ],
        ).model_dump(),
    )
