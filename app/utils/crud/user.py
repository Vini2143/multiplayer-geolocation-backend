import base64
from datetime import datetime, timedelta
import hashlib
import secrets
from typing import Any, Optional, Sequence
from uuid import UUID
from zoneinfo import ZoneInfo
from app.core.config import settings
import jwt
from sqlalchemy import func, select, update, delete, String
from sqlalchemy.orm import Session, InstrumentedAttribute

from app.core.security import get_password_hash, verify_password
from app.models import UserModel
from app.schemas.misc import LoginSchema
from app.schemas.users import UserCreateSchema

def authenticate_user(*, db_session: Session, payload: LoginSchema) -> UserModel | None:
    db_user = read_user_by_param(db_session=db_session, param=UserModel.username, value=payload.username)

    if not db_user:
        return None
    
    if not verify_password(payload.password, db_user.password):
        return None
    
    return db_user


def create_user(*, db_session: Session, payload: UserCreateSchema) -> UserModel:
    user = UserModel(**payload.model_dump())

    user.password = get_password_hash(payload.password)

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


def read_user_by_param(*, db_session: Session, param: InstrumentedAttribute, value) -> UserModel | None:
    query = select(UserModel).where(param == value)

    user = db_session.execute(query).scalar()

    return user

