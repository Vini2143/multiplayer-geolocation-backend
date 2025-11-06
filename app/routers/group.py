import uuid
from typing import Any, List
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from pydantic import ValidationError
from app.schemas.ws_event import WsEventSchema
from app.schemas.waypoint import WaypointCreateSchema, WaypointResponseSchema
from app.utils.deps import CurrentUser, SessionDep
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.models import GroupModel, WaypointModel
from app.schemas.misc import PaginatedList, Message
from app.schemas.group import GroupCreateSchema, GroupResponseSchema

from app.utils.websocket_manager import active_connections

router = APIRouter(prefix="/groups", tags=["groups"])


@router.post("/", response_model=GroupResponseSchema)
def create_group(*, db_session: SessionDep, current_user: CurrentUser, payload: GroupCreateSchema) -> Any:
    """
    Create new group.
    """

    group = GroupModel(user_owner_id=current_user.id, code=payload.name, **payload.model_dump())
    group.users.add(current_user)
    group.save(db_session)

    return group


@router.get("/{group_id}", response_model=GroupResponseSchema)
def get(*, db_session: SessionDep, current_user: CurrentUser, group_id: int) -> Any:
    """
    Get groups of current user.
    """

    group = GroupModel.first(db_session, id=group_id)

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

    group = GroupModel.first(db_session, id=group_id)

    if not group:
        raise HTTPException(
            status_code=404, detail="Object does not exists."
        )
    
    if current_user != group.user_owner:
        raise HTTPException(
            status_code=403, detail="You do not have permission to perform this action."
        )
    
    group.delete(db_session)

    return Message(message="Group successfully deleted.")




@router.post("/{group_id}/waypoints/", response_model=WaypointResponseSchema)
def create_waypoint(*, db_session: SessionDep, current_user: CurrentUser, group_id: int, payload: WaypointCreateSchema) -> Any:
    """
    Create new waypoint in a group.
    """

    waypoint = WaypointModel(group_id=group_id, **payload.model_dump())
    waypoint.save(db_session)

    ws_event = WsEventSchema(event_type="update_waypoint", data=WaypointResponseSchema(waypoint)).model_dump_json()
    active_connections.broadcast(waypoint.group_id, ws_event)

    return waypoint


@router.get("/{group_id}/waypoints/", response_model=List[WaypointResponseSchema])
def get_waypoints(*, db_session: SessionDep, current_user: CurrentUser, group_id: int) -> Any:
    """
    Get all waypoints of a group.
    """

    group = GroupModel.first(db_session, id=group_id)

    if current_user not in group.users:
        raise HTTPException(
            status_code=403, detail="You do not have permission to perform this action."
        )

    waypoints = group.waypoints

    return waypoints


@router.delete("/waypoints/{waypoint_id}", response_model=Message)
def delete_waypoint(*, db_session: SessionDep, current_user: CurrentUser, waypoint_id: int) -> Any:
    """
    Delete a waypoint.
    """

    waypoint = WaypointModel.first(db_session, id=waypoint_id)

    if not waypoint:
        raise HTTPException(
            status_code=404, detail="Object does not exists."
        )

    if current_user != waypoint.group.user_owner:
        raise HTTPException(
            status_code=403, detail="You do not have permission to perform this action."
        )
    
    waypoint.delete(db_session)

    return Message(message="Waypoint successfully deleted.")
