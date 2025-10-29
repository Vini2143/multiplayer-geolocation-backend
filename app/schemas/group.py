from datetime import datetime
from typing import Optional
from uuid import UUID
from ._base import OrmBaseSchema


class GroupCreateSchema(OrmBaseSchema):
    name: str


class GroupResponseSchema(OrmBaseSchema):
    id: int
    username: str
    lat: Optional[float]
    long: Optional[float]


