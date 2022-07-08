# from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLALCHEMY_DATABASE_URL = (
#     f"postgresql://{config('DB_USER')}:"
#     f"{config('DB_PASSWORD')}@{config('DB_HOST')}:"
#     f"{config('DB_PORT')}/{config('DB_NAME')}"
# )
SQLALCHEMY_DATABASE_URL = "sqlite:///./sqlite.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # noqa: E501
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
