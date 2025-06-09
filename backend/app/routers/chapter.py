from typing import Annotated

import anyio
from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

from ..dependencies.auth import get_current_active_user
from ..dependencies.chapter import get_extract_pdf_to_markdown, get_extract_chapter_text
from ..dependencies.db import get_db
from ..dependencies.google_drive import get_drive_service, get_upload_pdf
from ..models.user import User
from ..utils.logger import logger
from ..schemas.response import GenericResponse
from ..settings import settings

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
    extract_chapter_text=Depends(get_extract_chapter_text),
    file: UploadFile = File(...),
):
    # llm = ChatOpenAI(model="gpt-4.1", openai_api_key=settings.openai_api_key)

    # response = llm.invoke("What is the capital of Serbia?")

    # return GenericResponse(message=f"Response {response.content}", data=None)
    file_bytes = anyio.run(file.read)
    file_id, file_link = upload_pdf_to_drive(
        drive_service, file_bytes, current_user, chapter_name, "interaktivni"
    )
    markdown_text = extract_pdf_to_markdown(file_bytes, db)
    extracted_text = extract_chapter_text(markdown_text, chapter_name, db)
    return GenericResponse(
        message=f"Chapter '{chapter_name}' processed successfully.", data=extracted_text
    )
