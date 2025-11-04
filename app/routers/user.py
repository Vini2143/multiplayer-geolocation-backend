import uuid
from typing import Any
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from pydantic import ValidationError
from app.utils.deps import CurrentUser, SessionDep
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.models import UserModel
from app.schemas.misc import PaginatedList, Message
from app.schemas.user import UserLocationSchema, UserPasswordSchema, UserCreateSchema, UserResponseSchema

from app.utils.websocket_manager import active_connections


router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/", 
    response_model=UserResponseSchema
)
def create_user(*, db_session: SessionDep, payload: UserCreateSchema) -> Any:
    """
    Create new user.
    """

    user = UserModel.filter(db_session, username=payload.username)

    if user:
        raise HTTPException(
            status_code=409,
            detail="This username is already in use.",
        )
    
    user = UserModel(**payload.model_dump())
    user.password = get_password_hash(payload.password)

    user.save(db_session)

    return user


@router.patch("/me/password/", response_model=Message)
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
            status_code=400, detail="New password cannot be the same as the current one."
        )
    
    current_user.password = get_password_hash(payload.new_password)
    current_user.save(db_session)

    return Message(message="Password updated successfully.")


@router.get("/me/", response_model=UserResponseSchema)
def get_me(current_user: CurrentUser) -> Any:
    """
    Get current user.
    """
    return current_user


@router.patch("/me/location/", response_model=Message)
def update_location_me(
    *, db_session: SessionDep, payload: UserLocationSchema, current_user: CurrentUser
) -> Any:
    """
    Update own location.
    """

    current_user.lat = payload.lat
    current_user.long = payload.long

    current_user.save(db_session)

    for group in current_user.groups:
        active_connections.broadcast(group.id, UserResponseSchema(current_user).model_dump_json())

    return Message(message="Password updated successfully.")