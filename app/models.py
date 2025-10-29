from random import randbytes
from typing import Optional
from uuid import uuid4
from zoneinfo import ZoneInfo
from sqlalchemy import MetaData, ForeignKey, Integer, BigInteger, UUID, DateTime, UniqueConstraint, JSON
from sqlalchemy.orm import mapped_column, relationship, Mapped, DeclarativeBase, MappedAsDataclass
from datetime import datetime, date, timedelta
from app.enums import *
from sqlalchemy.ext.hybrid import hybrid_property
from app.core.config import settings



my_metadata = MetaData()

class Base(DeclarativeBase):
    pass


class UserModel(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    username: Mapped[str]
    password: Mapped[str]

    lat: Mapped[Optional[float]]
    long: Mapped[Optional[float]]


class GroupModel(Base):
    __tablename__ = "group"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_owner_id: Mapped[str] = mapped_column(ForeignKey("user.id"))

    name: Mapped[str]
    code: Mapped[str]


class _UserGroupModel(Base):
    __tablename__ = "user_group"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("user.id"))
    group_id: Mapped[str] = mapped_column(ForeignKey("group.id"))

    __table_args__ = (UniqueConstraint("user_id", "group_id"),)


class WaypointModel(Base):
    __tablename__ = "waypoint"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    group_id: Mapped[str] = mapped_column(ForeignKey("group.id"))

    name: Mapped[str]
    lat: Mapped[Optional[float]]
    long: Mapped[Optional[float]]


class _WaypointGroupModel(Base):
    __tablename__ = "waypoint_group"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    waypoint_id: Mapped[str] = mapped_column(ForeignKey("waypoint.id"))
    group_id: Mapped[str] = mapped_column(ForeignKey("group.id"))

    __table_args__ = (UniqueConstraint("waypoint_id", "group_id"),)
