from datetime import timedelta
import secrets
from typing import Annotated, Any
import base64
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from app.core import security
from app.core.config import settings
from app.core.security import get_password_hash
from urllib.parse import quote, urlencode
from app.models import UserModel
from app.utils.crud import user as user_crud
from app.schemas.misc import (
    LoginSchema,
    Message,
    TokenSchema,
)
from app.utils.deps import CurrentUser, SessionDep


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login/access-token")
def login_access_token(
    db_session: SessionDep, payload: LoginSchema
) -> TokenSchema:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    
    user = user_crud.authenticate_user(
        db_session=db_session, payload=payload
    )

    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    return TokenSchema(
        access_token=security.create_access_token(
            user.id, expires_delta=access_token_expires
        )
    )
