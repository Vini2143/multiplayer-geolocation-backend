import uuid
from typing import Any
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from pydantic import ValidationError
from app.schemas.user import UserPasswordSchema
from app.utils.deps import (
    CurrentUser,
    SessionDep,
)
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.models import GroupModel, UserModel
from app.schemas import (
    GroupCreateSchema,
    GroupResponseSchema,
    PaginatedList,
    Message,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/", 
    response_model=GroupResponseSchema
)
def create_group(*, db_session: SessionDep, current_user: CurrentUser, payload: GroupCreateSchema) -> Any:
    """
    Create new group.
    """

    group = GroupModel(user_owner_id=current_user.id, **payload)

    return group


@router.get("/me", response_model=GroupResponseSchema)
def read_user_me(current_user: CurrentUser) -> Any:
    """
    Get current user.
    """
    return current_user
