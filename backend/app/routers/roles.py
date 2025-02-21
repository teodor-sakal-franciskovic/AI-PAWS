from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from typing import List

from sqlalchemy.orm import Session

from ..schemas.response import GenericResponse
from ..schemas.roles import RoleResponse

from ..dependencies.db import get_db
from ..dependencies.roles import get_retrieve_roles


router = APIRouter(
    prefix="/roles",
    tags=["roles"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", tags=["roles"], response_model=GenericResponse)
def retrieve_roles(
    db: Session = Depends(get_db),
    retrieve_roles=Depends(get_retrieve_roles),
) -> GenericResponse:
    roles: List[RoleResponse] = retrieve_roles(db)
    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message="Successfully retrieved user roles", data=roles
        ).model_dump(),
    )
