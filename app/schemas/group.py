from datetime import datetime
from typing import List, Optional
from uuid import UUID
from ._base import OrmBaseSchema


class GroupCreateSchema(OrmBaseSchema):
    name: str


class GroupResponseSchema(OrmBaseSchema):
    id: int
    user_owner_id: int
    code: str
    name: str

