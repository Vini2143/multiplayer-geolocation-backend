import jwt
import socketio
from app.core import security
from app.models import UserModel
from app.core.config import settings
from app.schemas.user import UserResponseSchema
from app.core.database import engine
from sqlalchemy.orm import Session

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")


class PositionStorage:
    def __init__(self):
        self._storage = {}

    def set_user(self, sid: str, data: dict):
        self._storage[sid] = data

    def get_user(self, sid: str):
        return self._storage.get(sid)

    def remove_user(self, sid: str):
        self._storage.pop(sid, None)

    def commit(self):
        mappings = []

        for sid, user_data in self._storage.items():
            if user_data["lat"] is not None and user_data["long"] is not None:
                mappings.append({
                    "id": user_data["id"],
                    "lat": user_data["lat"],
                    "long": user_data["long"],
                })

        if not mappings:
            return

        with Session(engine) as db_session:
            db_session.bulk_update_mappings(UserModel, mappings)
            db_session.commit()

positions_storage = PositionStorage()


@sio.on("connect")
async def connect(sid, environ, auth):
    try:
        with Session(engine) as db_session:
            query = environ.get("QUERY_STRING", "")
            params = dict(p.split("=") for p in query.split("&") if "=" in p)
            token = params.get("token")
            group_id = params.get("group_id")


            if not token or not group_id:
                raise ValueError("Could not validate credentials.")

            token_data = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
            )
            user_id = int(token_data.get("sub"))

            user = UserModel.first(db_session, id=user_id)

            if not user:
                raise ValueError("User not found.")

            await sio.enter_room(sid, str(group_id))
            positions_storage.set_user(sid, UserResponseSchema.model_validate(user).model_dump())
            
            print(f"User {user.username} connected to group {group_id}.")

    except Exception as e:
        print(f"Error to connect: {e}")
        await sio.disconnect(sid)

@sio.on("client_update_position")
async def client_update(sid, data):
    positions_storage.set_user(sid, data)
    rooms = list(sio.rooms(sid))

    await sio.emit(
        "server_update_position",
        data=data,
        to=rooms,
    )


@sio.on("disconnect")
async def disconnect(sid, data):
    user_data = positions_storage.get_user(sid)
    rooms = list(sio.rooms(sid))

    print(f"User {user_data.get("username")} disconnected from group.")
    positions_storage.commit()
    positions_storage.remove_user(sid)

    await sio.emit(
        "client_disconnect",
        data=data,
        to=rooms,
    )

    
