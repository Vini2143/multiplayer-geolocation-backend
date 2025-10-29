from typing import Annotated
from fastapi import Depends
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings
from app.utils.crud import user as crud

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


SessionDep = Annotated[Session, Depends(get_db_session)]
