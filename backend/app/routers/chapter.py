
from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from ..dependencies.auth import get_current_active_user
from ..dependencies.chapter import get_extract_pdf_to_markdown
from ..dependencies.db import get_db
from ..models.user import User
from ..schemas.response import GenericResponse

router = APIRouter(
    prefix="/chapters",
    tags=["chapters"],
    responses={404: {"description": "Not found"}},
)


@router.post("/{chapter_name}/interactive", response_model=GenericResponse)
def upload_chapter_interactive(
    chapter_name: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
    extract_pdf_to_markdown=Depends(get_extract_pdf_to_markdown),
    file: UploadFile = File(...),
):
    markdown_text = extract_pdf_to_markdown(file, db)
    
    return GenericResponse(
        message=f"Chapter '{chapter_name}' processed successfully.",
        data=markdown_text
    )