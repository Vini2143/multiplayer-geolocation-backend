
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, status
import jwt
from pydantic import ValidationError
from app.core import security
from app.models import UserModel
from app.utils.deps import SessionDep
from app.core.config import settings
from app.utils.websocket_manager import ConnectionManager
ws_router = APIRouter(prefix="/ws", tags=["ws"])
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List

ws_router = APIRouter()
active_connections = ConnectionManager()


@ws_router.websocket("/ws/location/{group_id}")
async def websocket_location(websocket: WebSocket, db_session: SessionDep, group_id: int, token: str):

    try:
        token_data = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )

    except (jwt.InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
        )

    current_user = UserModel.first(db_session, id=int(token_data.get("sub")))

    await active_connections.connect(group_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()

            await active_connections.broadcast(group_id, {
                "user": current_user.username,
                "data": data,
            })
    except WebSocketDisconnect:
        active_connections.disconnect(group_id, websocket)
        print(f"{current_user.username} was left.")
