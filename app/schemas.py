from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict

from app.permissions.roles import Role
from app.security import get_password_hash


class UserSignUp(BaseModel):
    email: EmailStr
    password: str | None = None
    name: str
    surname: str | None = None
    role: Role

    @property
    def password_hash(self):
        return get_password_hash(self.password)


class UserUpdate(BaseModel):
    name: str | None = None
    surname: str | None = None
    roles: Role | None = None


class User(BaseModel):
    email: EmailStr
    name: str
    surname: str | None = None
    role: Role
    register_date: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class ItemIn(BaseModel):
    name: str


class ItemUpdate(BaseModel):
    name: str


class Item(ItemIn):
    id: int

    model_config = ConfigDict(from_attributes=True)
