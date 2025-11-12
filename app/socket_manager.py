import jwt
import socketio
from app.core import security
from app.models import UserModel
from app.core.config import settings
from app.schemas.user import UserResponseSchema
from app.core.database import engine
from sqlalchemy.orm import Session

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")

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

            current_user = UserModel.first(db_session, id=user_id)

            if not current_user:
                raise ValueError("User not found.")

            await sio.enter_room(sid, str(group_id))
            
            print(f"User {current_user.username} connected to group {group_id}")

    except Exception as e:
        print(f"Error to connect: {e}")
        await sio.disconnect(sid)


@sio.on("disconnect")
async def disconnect(sid):
    print(f"Client {sid} left.")
