import uuid
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from pydantic import ValidationError

from app.schemas.user import UserPasswordSchema
from app.utils.crud import user as user_crud
from app.utils.deps import (
    CurrentUser,
    SessionDep,
)
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.models import UserModel
from app.schemas import (
    UserCreateSchema,
    UserResponseSchema,
    PaginatedList,
    Message,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/", 
    response_model=UserResponseSchema
)
def create_user(*, db_session: SessionDep, payload: UserCreateSchema) -> Any:
    """
    Create new user.
    """

    user = user_crud.read_user_by_param(db_session=db_session, param=UserModel.username, value=payload.username)

    if user:
        raise HTTPException(
            status_code=409,
            detail="The user with this email already exists in the system.",
        )

    user = user_crud.create_user(db_session=db_session, payload=payload)

    return user


@router.patch("/me/password", response_model=Message)
def update_password_me(
    *, db_session: SessionDep, payload: UserPasswordSchema, current_user: CurrentUser
) -> Any:
    """
    Update own password.
    """

    if not verify_password(payload.current_password, current_user.password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    
    if payload.current_password == payload.new_password:
        raise HTTPException(
            status_code=400, detail="New password cannot be the same as the current one"
        )
    
    hashed_password = get_password_hash(payload.new_password)

    data = {"password": hashed_password}

    user_crud.update_user(db_session=db_session, db_user=current_user, data=data)
    
    return Message(message="Password updated successfully")


@router.get("/me", response_model=UserResponseSchema)
def read_user_me(current_user: CurrentUser) -> Any:
    """
    Get current user.
    """
    return current_user
