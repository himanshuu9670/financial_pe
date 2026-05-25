"""Role-based access control."""

from enum import Enum

from fastapi import HTTPException, status


class Role(str, Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


ROLE_HIERARCHY = {
    Role.VIEWER: 0,
    Role.EDITOR: 1,
    Role.ADMIN: 2,
}


def role_at_least(user_role: str, required: Role) -> bool:
    try:
        current = Role(user_role)
    except ValueError:
        return False
    return ROLE_HIERARCHY.get(current, 0) >= ROLE_HIERARCHY[required]


def require_role(user_role: str, required: Role) -> None:
    if not role_at_least(user_role, required):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Requires {required.value} role or higher",
        )


def can_edit(user_role: str) -> bool:
    return role_at_least(user_role, Role.EDITOR)


def can_export(user_role: str) -> bool:
    return role_at_least(user_role, Role.EDITOR)


def can_admin(user_role: str) -> bool:
    return role_at_least(user_role, Role.ADMIN)
