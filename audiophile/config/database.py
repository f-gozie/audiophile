from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from audiophile.config.configuration import settings

SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{settings.DB_USER}:"
    f"{settings.DB_PASSWORD}@{settings.DB_HOST}:"
    f"{settings.DB_PORT}/{settings.DB_NAME}"
)
# SQLALCHEMY_DATABASE_URL = "sqlite:///./sqlite.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)  # noqa: E501
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
