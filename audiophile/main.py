from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from . import models, schema, workers
from .database import SessionLocal, engine
from .tasks import generate_predictions

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def refresh_predictions():
    scheduler = BackgroundScheduler()
    scheduler.add_job(generate_predictions, "interval", seconds=1)
    scheduler.start()


@app.get("/api/files/{file_id}/", response_model=schema.File)
def get_file_details(file_id: int, db: Session = Depends(get_db)):
    """Get detail for a given file_id"""
    predictions = workers.get_file(db, file_id)
    return predictions
