from fastapi import APIRouter
from app.core.config import settings
from . import (
    auth,
    user

)

api_router = APIRouter(prefix=settings.API_V1_STR)

api_router.include_router(auth.router)
api_router.include_router(user.router)

