import json

from typing import Annotated, List

from fastapi import APIRouter, Body, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..dependencies.auth import require_role
from ..dependencies.db import get_db
from ..models.role import Role
from ..schemas.group import GroupCreate, GroupResponse
from ..schemas.response import GenericResponse
from ..services.group import create_group, retrieve_active_groups

router = APIRouter(
    prefix="/groups",
    tags=["groups"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_group_endpoint(
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
    role: Annotated[Role, Depends(require_role("Instructor"))],
    db: Session = Depends(get_db),
):
    create_group(group, db)
    return JSONResponse(
        status_code=201,
        content=GenericResponse(
            message="Successfully created a new group.", data=None
        ).model_dump(),
    )


@router.get("/", tags=["groups"], response_model=GenericResponse)
def retrieve_active_groups_endpoint(
    db: Session = Depends(get_db),
) -> GenericResponse:
    active_groups: List[GroupResponse] = retrieve_active_groups(db)
    return JSONResponse(
        status_code=200,
        content=json.loads(
            GenericResponse(
                message="Successfully retrieved active groups", data=active_groups
            ).model_dump_json()
        ),
    )
