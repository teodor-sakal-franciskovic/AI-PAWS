from typing import Annotated

from fastapi import APIRouter, Body, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..dependencies.auth import require_role
from ..dependencies.db import get_db
from ..dependencies.group import get_create_group
from ..models.role import Role
from ..schemas.group import GroupCreate
from ..schemas.response import GenericResponse

router = APIRouter(
    prefix="/groups",
    tags=["groups"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_group(
    group: Annotated[
        GroupCreate,
        Body(
            examples=[
                {
                    "name": "G_1_2025",
                    "valid_from": "2025-01-01T00:00:00",
                    "valid_until": "2025-12-31T23:59:59",
                }
            ]
        ),
    ],
    role: Annotated[Role, Depends(require_role("TA"))],
    create_group=Depends(get_create_group),
    db: Session = Depends(get_db),
):
    create_group(group, db)

    return JSONResponse(
        status_code=201,
        content=GenericResponse(
            message="Successfully created a new group.", data=None
        ).model_dump(),
    )
