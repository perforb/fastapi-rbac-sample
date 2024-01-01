from enum import StrEnum

from app.permissions import Permission


class Role(StrEnum):
    ADMINISTRATOR = "ADMINISTRATOR"
    USER = "USER"

    @classmethod
    def get_roles(cls):
        values = []
        for member in cls:
            values.append(f"{member.value}")
        return values


ROLE_PERMISSIONS = {
    Role.ADMINISTRATOR: [
        [
            Permission.USERS_CREATE,
            Permission.USERS_READ,
            Permission.USERS_UPDATE,
            Permission.USERS_DELETE,
        ],
        [
            Permission.ITEMS_CREATE,
            Permission.ITEMS_READ,
            Permission.ITEMS_UPDATE,
            Permission.ITEMS_DELETE,
        ]
    ],
    Role.USER: [
        [
            Permission.ITEMS_CREATE,
            Permission.ITEMS_READ,
            Permission.ITEMS_UPDATE,
        ]
    ]
}


def get_role_permissions(role: Role):
    permissions = set()
    for permissions_group in ROLE_PERMISSIONS[role]:
        for permission in permissions_group:
            permissions.add(str(permission))
    return list(permissions)
