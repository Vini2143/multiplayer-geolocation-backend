import re
from collections.abc import Generator
from enum import Enum
from typing import Annotated
import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core import security
from app.core.config import settings
from app.core.database import engine
from app.models import UserModel

def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(HTTPBearer())]


def get_current_user(db_session: SessionDep, token: TokenDep) -> UserModel:
    try:
        token_data = jwt.decode(
            token.credentials, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )

    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
        )

    user = db_session.get(UserModel, token_data.get("sub"))

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user.")

    return user


CurrentUser = Annotated[UserModel, Depends(get_current_user)]

