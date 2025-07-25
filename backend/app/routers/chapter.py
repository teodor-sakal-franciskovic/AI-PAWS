from typing import List

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..dependencies.db import get_db
from ..dependencies.chapter import get_retrieve_chapters
from ..schemas.response import GenericResponse
from ..schemas.chapter import ChapterResponse

router = APIRouter(
    prefix="/chapters",
    tags=["chapters"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=GenericResponse)
def retrieve_chapters(
    db: Session = Depends(get_db),
    retrieve_chapters=Depends(get_retrieve_chapters),
):
    chapters: List[ChapterResponse] = retrieve_chapters(db)
    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message="Successfully retrieved chapters", data=chapters
        ).model_dump(),
    )
