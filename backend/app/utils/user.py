from ..models.role import Role
from ..models.user import User
from ..schemas.user import UserResponse


def create_user_response(user: User, role: Role):
    return UserResponse(
        email=user.email,
        name=user.name,
        surname=user.surname,
        is_active=user.is_active,
        role=role.name,
    )
