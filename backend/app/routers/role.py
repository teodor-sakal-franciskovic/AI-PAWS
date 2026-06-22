from typing import List

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..dependencies.db import get_db
from ..schemas.response import GenericResponse
from ..schemas.role import RoleResponse
from ..services.role import retrieve_roles

router = APIRouter(
    prefix="/roles",
    tags=["roles"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", tags=["roles"], response_model=GenericResponse)
def retrieve_roles_endpoint(
    db: Session = Depends(get_db),
) -> GenericResponse:
    roles: List[RoleResponse] = retrieve_roles(db)
    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message="Successfully retrieved user roles", data=roles
        ).model_dump(),
    )
