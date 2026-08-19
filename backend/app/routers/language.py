from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..dependencies.auth import require_role
from ..dependencies.db import get_db
from ..models.role import Role
from ..schemas.language import LanguageResponse
from ..schemas.response import GenericResponse
from ..services.language import retrieve_languages

router = APIRouter(
    prefix="/languages",
    tags=["languages"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=GenericResponse)
def retrieve_languages_endpoint(
    role: Annotated[Role, Depends(require_role("Instructor"))],
    db: Session = Depends(get_db),
) -> GenericResponse:
    languages: list[LanguageResponse] = retrieve_languages(db)
    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message="Successfully retrieved languages",
            data=[language.model_dump(mode="json") for language in languages],
        ).model_dump(),
    )
