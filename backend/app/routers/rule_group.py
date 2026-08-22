from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session

from ..dependencies.auth import get_current_active_user, require_role
from ..dependencies.db import get_db
from ..exceptions import ApiError
from ..models.role import Role
from ..models.user import User
from ..schemas.response import GenericResponse, IdResponse, NameAvailabilityResponse
from ..schemas.rule_group import (
    RuleGroupCreate,
    RuleGroupDetailResponse,
    RuleGroupUpdate,
)
from ..services.rule_group import (
    create_rule_group,
    delete_rule_group,
    get_all_rule_groups,
    get_rule_group_detail,
    is_name_available,
    update_rule_group,
)
from ..tasks.rule_group import generate_prompt_descriptions

router = APIRouter(
    prefix="/rule-groups",
    tags=["rule-groups"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=GenericResponse, status_code=201)
def create_rule_group_endpoint(
    data: RuleGroupCreate,
    background_tasks: BackgroundTasks,
    role: Annotated[Role, Depends(require_role("Instructor"))],
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    rule_group_id = create_rule_group(db, data, current_user.id)
    background_tasks.add_task(generate_prompt_descriptions, rule_group_id)
    return JSONResponse(
        status_code=201,
        content=GenericResponse(
            message="Rule group successfully created. Prompt descriptions are being generated in the background.",
            data=IdResponse(id=rule_group_id).model_dump(),
        ).model_dump(),
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
                RuleGroupDetailResponse.model_validate(rule_group).model_dump(
                    mode="json"
                )
                for rule_group in rule_groups
            ],
        ).model_dump(),
    )


@router.get("/check-name", response_model=GenericResponse)
def check_rule_group_name_endpoint(
    role: Annotated[Role, Depends(require_role("Instructor"))],
    name: str,
    exclude_id: int | None = None,
    db: Session = Depends(get_db),
):
    available = is_name_available(db, name, exclude_id)
    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message="Successfully checked rule group name availability.",
            data=NameAvailabilityResponse(name_available=available).model_dump(),
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
        raise ApiError(404, "RULE_GROUP_NOT_FOUND", "Rule group not found.")
    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message="Successfully retrieved rule group.",
            data=RuleGroupDetailResponse.model_validate(rule_group).model_dump(
                mode="json"
            ),
        ).model_dump(),
    )


@router.put("/{rule_group_id}", status_code=204)
def update_rule_group_endpoint(
    rule_group_id: int,
    data: RuleGroupUpdate,
    background_tasks: BackgroundTasks,
    role: Annotated[Role, Depends(require_role("Instructor"))],
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    rule_ids = update_rule_group(db, rule_group_id, data, current_user.id)
    if rule_ids:
        background_tasks.add_task(generate_prompt_descriptions, rule_group_id)
    return Response(status_code=204)


@router.delete("/{rule_group_id}", status_code=204)
def delete_rule_group_endpoint(
    rule_group_id: int,
    role: Annotated[Role, Depends(require_role("Instructor"))],
    db: Session = Depends(get_db),
):
    delete_rule_group(db, rule_group_id)
    return Response(status_code=204)
