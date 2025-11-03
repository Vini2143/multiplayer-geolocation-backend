from typing import Annotated
from fastapi import APIRouter, Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware
import jwt
from pydantic import ValidationError
from app.core import security
from app.models import UserModel
from app.core.config import settings
from app.utils.deps import CurrentUser, SessionDep, get_current_user
from app.routes import api_router


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

