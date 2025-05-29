from typing import Annotated

import anyio
from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from ..dependencies.auth import get_current_active_user
from ..dependencies.chapter import get_extract_pdf_to_markdown
from ..dependencies.db import get_db
from ..dependencies.google_drive import get_drive_service, get_upload_pdf
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
    drive_service=Depends(get_drive_service),
    upload_pdf_to_drive=Depends(get_upload_pdf),
    extract_pdf_to_markdown=Depends(get_extract_pdf_to_markdown),
    file: UploadFile = File(...),
):
    file_bytes = anyio.run(file.read)
    dict = upload_pdf_to_drive(
        drive_service, file_bytes, current_user, chapter_name, "interaktivni"
    )
    markdown_text = extract_pdf_to_markdown(file_bytes, db)

    return GenericResponse(
        message=f"Chapter '{chapter_name}' processed successfully.", data=markdown_text
    )
