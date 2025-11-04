from datetime import datetime
from typing import Optional
from uuid import UUID
from ._base import OrmBaseSchema


class UserCreateSchema(OrmBaseSchema):
    username: str
    password: str


class UserResponseSchema(OrmBaseSchema):
    id: int
    username: str
    lat: Optional[float]
    long: Optional[float]


class UserPasswordSchema(OrmBaseSchema):
    current_password: str
    new_password: str


class UserLocationSchema(OrmBaseSchema):
    lat: Optional[float]
    long: Optional[float]
