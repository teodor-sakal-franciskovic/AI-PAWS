from typing import Annotated
from urllib.parse import quote

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from ..dependencies.auth import get_current_active_user, require_role
from ..dependencies.db import get_db
from ..models.role import Role
from ..models.user import User
from ..services.evaluation import PDF_MIME_TYPE, get_submission_file

router = APIRouter(
    prefix="/submissions",
    tags=["submissions"],
    responses={404: {"description": "Not found"}},
)


@router.get("/{submission_id}/file")
def download_submission_file_endpoint(
    submission_id: int,
    role: Annotated[Role, Depends(require_role("Instructor"))],
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    file_bytes, file_name = get_submission_file(db, submission_id, current_user.id)
    return Response(
        content=file_bytes,
        media_type=PDF_MIME_TYPE,
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{quote(file_name)}"
        },
    )
