from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import User
from app.schemas import UserSignUp, UserUpdate


class DuplicateError(Exception):
    pass


def add_user(db: Session, user: UserSignUp):
    user = User(
        email=user.email,
        password=user.password_hash,
        name=user.name,
        surname=user.surname,
        role=user.role
    )
    try:
        db.add(user)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise DuplicateError(f"Email {user.email} is already attached to a registered user.")
    return user


def get_user(db: Session, email: str) -> User:
    user = db.scalar(
        select(User)
        .where(User.email == email)
    )
    return user


def get_users(db: Session) -> list[User]:
    users = list(db.scalars(
        select(User)
    ))
    return users


def update_user(db: Session, email: str, user_update: UserUpdate):
    user = db.scalar(
        select(User)
        .where(User.email == email)
    )
    if not user:
        raise ValueError(
            f"There isn't any user with username {email}")

    updated_user = user_update.model_dump(exclude_unset=True)
    for key, value in updated_user.items():
        setattr(user, key, value)
    db.commit()
    return user


def delete_user(db: Session, email: str):
    user = db.scalar(
        select(User)
        .where(User.email == email)
    )
    if not user:
        raise ValueError(f"There is no user with email {email}")
    else:
        user.delete()
        db.commit()
