from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from . import models, schema, workers
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/api/files/{file_id}/predictions", response_model=schema.File)
def read_predictions(
    file_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),  # noqa: E501
):
    """Get all predictions for a given file_id"""
    predictions = workers.get_file_predictions(db, file_id, skip, limit)
    return predictions
