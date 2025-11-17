import asyncio
import jwt
import socketio
from app.core import security
from app.models import UserModel
from app.core.config import settings
from app.schemas.user import UserResponseSchema
from app.core.database import engine
from sqlalchemy.orm import Session

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")

class PositionManager:

    def __init__(self, sio: socketio.AsyncServer):
        self.sio = sio
        self._storage: dict[str, dict] = {} 
        self._sid_map: dict[int, str] = {} 
        self._disconnect_tasks: dict[int, asyncio.Task] = {}


    def set_user(self, sid: str, data: dict):
        user_id = data.get("id")
        old_sid = self._sid_map.get(user_id)

        if old_sid and old_sid != sid:
            self._storage.pop(old_sid, None)

        self._sid_map[user_id] = sid
        self._storage[sid] = data

        task = self._disconnect_tasks.pop(user_id, None)
        if task and not task.done():
            task.cancel()

    def get_user(self, sid: str):
        return self._storage.get(sid)

    def get_user_sid(self, user_id: int):
        return self._sid_map.get(user_id)
    
    def commit(self, user_data):
        user_id = user_data.get("id")
        if not user_id:
            return
        
        with Session(engine) as db_session:
            user = UserModel.first(db_session, id=user_id)
            if user:
                user.lat = user_data.get("lat")
                user.long = user_data.get("long")
                user.save(db_session)


    async def update_position(self, sid: str, data: dict):
        self.set_user(sid, data)
        rooms = list(self.sio.rooms(sid))
        await self.sio.emit("server_update_position", data=data, to=rooms)


    async def remove_user(self, sid: str, delay: int = 10):
        try:
            await asyncio.sleep(delay)
        except:
            return

        user_data = self._storage.pop(sid, None)
        if not user_data:
            return

        user_id = user_data.get("id")
        if self._sid_map.get(user_id) == sid:
            self._sid_map.pop(user_id, None)

        try:
            self.commit(user_data)
        except Exception as e:
            print(f"Error in commit user position: {e}")
            
        rooms = list(self.sio.rooms(sid))
        await self.sio.emit("client_disconnect", data=user_data, to=rooms)
    

    def cancelable_remove_user(self, sid: str, delay: int = 10):
        user_id = self.get_user(sid).get("id") if self.get_user(sid) else None
        if not user_id:
            return

        task = asyncio.create_task(self.remove_user(sid, delay))
        self._disconnect_tasks[user_id] = task

    async def broadcast_server_data(self, group_id):
        clients = self.sio.manager.rooms.get("/", {}).get(group_id, set())
        data = [self._storage.get(sid) for sid in clients if self._storage.get(sid)]
        await self.sio.emit("server_data", data=data, to=group_id)

        

manager = PositionManager(sio)


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
            manager.set_user(sid, UserResponseSchema.model_validate(user).model_dump())
            await manager.broadcast_server_data(str(group_id))
            
            print(f"User {user.username} connected to group {group_id}.")
    except Exception as e:
        print(f"Error to connect: {e}")
        await sio.disconnect(sid)


@sio.on("client_update_position")
async def client_update(sid, data):
    await manager.update_position(sid, data)

@sio.on("client_stop_sharing")
async def client_update(sid, data):
    await manager.remove_user(sid, 0)

@sio.on("disconnect")
async def disconnect(sid):
    manager.cancelable_remove_user(sid, delay=10)