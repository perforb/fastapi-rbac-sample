from fastapi import Depends, APIRouter, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import AuthorizationHandler, create_access_token, authenticate_user
from app.crud import users as crud
from app.database import get_db
from app.permissions import Permission
from app.schemas import User, UserSignUp, Token, UserUpdate

router = APIRouter(prefix="/v1")


@router.post("/token", response_model=Token, summary="Authorize as a user", tags=["Users"])
def authorize(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Logs in a user.
    """
    print(form_data.username)
    print(form_data.password)
    user = authenticate_user(db=db, user_email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=401, detail="Invalid user email or password.")
    try:
        access_token = create_access_token(data=user.email)
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred. Report this message to support: {e}")


@router.post("/users",
             dependencies=[Depends(AuthorizationHandler([Permission.USERS_CREATE]))],
             response_model=User, summary="Register a user", tags=["Users"])
def create_user(user_signup: UserSignUp, db: Session = Depends(get_db)):
    """
    Registers a user.
    """
    try:
        user_created = crud.add_user(db, user_signup)
        return user_created
    except crud.DuplicateError as e:
        raise HTTPException(status_code=403, detail=f"{e}")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred. Report this message to support: {e}")


@router.get("/users",
            dependencies=[Depends(AuthorizationHandler([Permission.USERS_READ]))],
            response_model=list[User], summary="Get all users", tags=["Users"])
def get_users(db: Session = Depends(get_db)):
    """
    Returns all users.
    """
    try:
        users = crud.get_users(db)
        return users
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred. Report this message to support: {e}")


@router.patch("/users",
              dependencies=[Depends(AuthorizationHandler([Permission.USERS_CREATE, Permission.USERS_UPDATE]))],
              response_model=User,
              summary="Update a user", tags=["Users"])
def update_user(user_email: str, user_update: UserUpdate, db: Session = Depends(get_db)):
    """
    Updates a user.
    """
    try:
        user = crud.update_user(db, user_email, user_update)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=404, detail=f"{e}")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred. Report this message to support: {e}")


@router.delete("/users",
               dependencies=[Depends(AuthorizationHandler([Permission.USERS_DELETE]))],
               summary="Delete a user", tags=["Users"])
def delete_user(user_email: str, db: Session = Depends(get_db)):
    """
    Deletes a user.
    """
    try:
        crud.delete_user(db, user_email)
        return {"result": f"User with email {user_email} has been deleted successfully!"}
    except ValueError as e:
        raise HTTPException(
            status_code=404, detail=f"{e}")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred. Report this message to support: {e}")
