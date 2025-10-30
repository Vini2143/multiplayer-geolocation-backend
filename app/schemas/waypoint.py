from datetime import datetime
from typing import Optional
from uuid import UUID
from ._base import OrmBaseSchema


class WaypointCreateSchema(OrmBaseSchema):
    name: str
    lat: float
    long: float


class WaypointResponseSchema(OrmBaseSchema):
    id: int
    name: str
    lat: float
    long: float