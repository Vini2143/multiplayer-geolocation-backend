import uuid
from typing import Any, List
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from pydantic import ValidationError
from app.utils.deps import CurrentUser, SessionDep
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.models import GroupModel, UserModel
from app.schemas.misc import PaginatedList, Message
from app.schemas.group import GroupCreateSchema, GroupResponseSchema

router = APIRouter(prefix="/groups", tags=["groups"])


@router.post("/", response_model=GroupResponseSchema)
def create_group(*, db_session: SessionDep, current_user: CurrentUser, payload: GroupCreateSchema) -> Any:
    """
    Create new group.
    """

    group = GroupModel(user_owner_id=current_user.id, code=payload.name, **payload.model_dump())
    group.users.append(current_user)
    group.save(db_session)

    return group


@router.get("/{group_id}", response_model=GroupResponseSchema)
def get(*, db_session: SessionDep, current_user: CurrentUser, group_id: int) -> Any:
    """
    Get groups of current user.
    """

    group = GroupModel.first(db_session=db_session, id=group_id)

    if current_user not in group.users:
        raise HTTPException(
            status_code=403, detail="You do not have permission to perform this action."
        )

    return group


@router.get("/me/", response_model=List[GroupResponseSchema])
def get_me_groups(current_user: CurrentUser) -> Any:
    """
    Get groups of current user.
    """

    groups = current_user.groups

    return groups


@router.delete("/{group_id}", response_model=Message)
def delete(*, db_session: SessionDep, current_user: CurrentUser, group_id: int) -> Any:
    """
    Delete a group.
    """

    group = GroupModel.first(db_session=db_session, id=group_id)

    if not group:
        raise HTTPException(
            status_code=404, detail="Object does not exists."
        )
    
    if group.user_owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="You do not have permission to perform this action."
        )

    return Message(message="Group successfully deleted.")

