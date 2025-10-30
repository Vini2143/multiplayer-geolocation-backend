from random import randbytes
from typing import Optional
from uuid import uuid4
from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session, InstrumentedAttribute
from sqlalchemy import MetaData, ForeignKey, Integer, BigInteger, UUID, DateTime, UniqueConstraint, JSON, select
from sqlalchemy.orm import mapped_column, relationship, Mapped, DeclarativeBase, MappedAsDataclass
from datetime import datetime, date, timedelta
from app.enums import *
from sqlalchemy.ext.hybrid import hybrid_property
from app.core.config import settings



my_metadata = MetaData()

class Base(DeclarativeBase):

    @classmethod
    def all(cls, db_session: Session):
        return db_session.scalars(select(cls)).all()

    @classmethod
    def filter(cls, db_session: Session, **kwargs):
        stmt = select(cls)
        for field, value in kwargs.items():
            stmt = stmt.where(getattr(cls, field) == value)
        return db_session.scalars(stmt).all()

    @classmethod
    def first(cls, db_session: Session, **kwargs):
        stmt = select(cls)
        for field, value in kwargs.items():
            stmt = stmt.where(getattr(cls, field) == value)
        return db_session.scalars(stmt).first()

    def save(self, db_session: Session):
        db_session.add(self)
        db_session.commit()
        db_session.refresh(self)

    def delete(self, db_session: Session):
        db_session.delete(self)
        db_session.commit()



class UserModel(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    username: Mapped[str]
    password: Mapped[str]

    lat: Mapped[Optional[float]]
    long: Mapped[Optional[float]]


class WaypointModel(Base):
    __tablename__ = "waypoint"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("group.id"))

    name: Mapped[str]
    lat: Mapped[Optional[float]]
    long: Mapped[Optional[float]]


class GroupModel(Base):
    __tablename__ = "group"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_owner_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    name: Mapped[str]
    code: Mapped[str]

    users: Mapped[set["UserModel"]] = relationship(
        backref="groups",
        secondary="user_group"
    )

    waypoints: Mapped[set["WaypointModel"]] = relationship(
        backref="waypoints",
        secondary="waypoint_group"
    )


class _UserGroupModel(Base):
    __tablename__ = "user_group"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    group_id: Mapped[int] = mapped_column(ForeignKey("group.id"))

    __table_args__ = (UniqueConstraint("user_id", "group_id"),)


class _WaypointGroupModel(Base):
    __tablename__ = "waypoint_group"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    waypoint_id: Mapped[int] = mapped_column(ForeignKey("waypoint.id"))
    group_id: Mapped[int] = mapped_column(ForeignKey("group.id"))

    __table_args__ = (UniqueConstraint("waypoint_id", "group_id"),)
