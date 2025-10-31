from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware
import jwt
from pydantic import ValidationError
from app.core import security
from app.models import UserModel
from app.routers import api_router
from app.core.config import settings
from app.utils.deps import CurrentUser, SessionDep, get_current_user


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)



@app.websocket("/ws")
async def websocket_location(websocket: WebSocket, db_session: SessionDep, token: str):

    try:
        token_data = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )

    except (jwt.InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
        )

    current_user = db_session.get(UserModel, token_data.get("sub"))

    print(current_user.id)

    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()
            print(data)
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        print("Connection closed")
