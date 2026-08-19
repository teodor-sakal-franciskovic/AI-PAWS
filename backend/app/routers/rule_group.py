from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..dependencies.auth import require_role
from ..dependencies.db import get_db
from ..models.role import Role
from ..schemas.response import GenericResponse
from ..schemas.rule_group import (
    RuleGroupDetailResponse,
    RuleGroupListItemResponse,
    RuleGroupNameCheckResponse,
)
from ..services.rule_group import (
    check_rule_group_name,
    get_all_rule_groups,
    get_rule_group_detail,
)

router = APIRouter(
    prefix="/rule-groups",
    tags=["rule-groups"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=GenericResponse)
def get_all_rule_groups_endpoint(
    role: Annotated[Role, Depends(require_role("Instructor"))],
    db: Session = Depends(get_db),
):
    rule_groups = get_all_rule_groups(db)
    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message="Successfully retrieved rule groups.",
            data=[
                RuleGroupListItemResponse.model_validate(rule_group).model_dump(
                    mode="json"
                )
                for rule_group in rule_groups
            ],
        ).model_dump(),
    )


@router.get("/name/{name}", response_model=GenericResponse)
def check_rule_group_name_endpoint(
    name: str,
    role: Annotated[Role, Depends(require_role("Instructor"))],
    exclude_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    used = check_rule_group_name(db, name, exclude_id)
    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message="Successfully checked rule group name availability.",
            data=RuleGroupNameCheckResponse(rule_name_used=used).model_dump(),
        ).model_dump(),
    )


@router.get("/{rule_group_id}", response_model=GenericResponse)
def get_rule_group_by_id_endpoint(
    rule_group_id: int,
    role: Annotated[Role, Depends(require_role("Instructor"))],
    db: Session = Depends(get_db),
):
    rule_group = get_rule_group_detail(db, rule_group_id)
    if not rule_group:
        raise HTTPException(status_code=404, detail="Rule group not found")
    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message="Successfully retrieved rule group.",
            data=RuleGroupDetailResponse.model_validate(rule_group).model_dump(
                mode="json"
            ),
        ).model_dump(),
    )
