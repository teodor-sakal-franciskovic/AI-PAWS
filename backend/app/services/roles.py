from typing import List
from sqlalchemy.orm import Session

from ..models.role import Role

from ..schemas.roles import RoleResponse

from ..repository.roles import retrieve_all


def retrieve_roles(db: Session):
    roles: List[Role] = retrieve_all(db)
    return [RoleResponse(id=role.id, name=role.name) for role in roles]
