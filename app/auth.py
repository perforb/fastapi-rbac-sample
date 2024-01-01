from datetime import datetime, timedelta, UTC

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from jose.jwt import encode, decode
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.crud.users import get_user
from app.database import get_db
from app.models import User
from app.permissions import Permission
from app.roles import get_role_permissions
from app.security import verify_password


class BearAuthException(Exception):
    pass


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "dummy_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(data: str):
    to_encode = {"sub": data}
    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_token_payload(token: str = Depends(oauth2_scheme)):
    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        payload_sub: str = payload.get("sub")
        if payload_sub is None:
            raise BearAuthException("Token could not be validated")
        return payload_sub
    except JWTError:
        raise BearAuthException("Token could not be validated")


def authenticate_user(db: Session, user_email: str, password: str):
    user = get_user(db, user_email)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        user_email = get_token_payload(token)
    except BearAuthException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate bearer token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user = get_user(db, user_email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized, could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user


class PermissionChecker:
    def __init__(self, permissions_required: list[Permission]):
        self.permissions_required = permissions_required

    def __call__(self, user: User = Depends(get_current_user)):
        for permission_required in self.permissions_required:
            if permission_required not in get_role_permissions(user.role):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions to access this resource")
        return user
