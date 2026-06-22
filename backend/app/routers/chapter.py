from typing import List

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..dependencies.db import get_db
from ..schemas.response import GenericResponse
from ..schemas.chapter import ChapterResponse
from ..services.chapter import retrieve_chapters

router = APIRouter(
    prefix="/chapters",
    tags=["chapters"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=GenericResponse)
def retrieve_chapters_endpoint(
    db: Session = Depends(get_db),
):
    chapters: List[ChapterResponse] = retrieve_chapters(db)
    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message="Successfully retrieved chapters", data=chapters
        ).model_dump(),
    )
