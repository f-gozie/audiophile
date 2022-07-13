from typing import Any, List

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import Depends, FastAPI, File, UploadFile
from sqlalchemy.orm import Session

from audiophile.config.database import SessionLocal, engine

from . import models, schema, workers
from .config.configuration import settings
from .services.buckets import S3Service
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
    scheduler.add_job(generate_predictions, "interval", minutes=2)
    scheduler.start()


@app.post("/api/files/upload/s3")
async def s3_upload(file: UploadFile = File(...)):
    """Create a new file in s3 bucket

    Args:
        file: The file to be uploaded

    Returns:
        A success message if file was uploaded successfully
    """
    s3_client = S3Service(
        bucket_name=settings.AWS_S3_BUCKET,
        region_name=settings.AWS_REGION,
        access_key=settings.AWS_ACCESS_KEY_ID,
        secret_key=settings.AWS_SECRET_ACCESS_KEY,
    )
    await workers.upload_file_to_s3(file, s3_client)
    return {"status": "Uploaded successfully"}


@app.post("/api/files/upload")
def local_upload(file: UploadFile = File(...)):
    """Upload a new file to local storage

    Args:
        file: The file to be uploaded

    Returns:
        A success message if file was uploaded successfully
    """
    response = workers.upload_file_to_local(file, settings.FILE_PATH)
    return response


@app.get("/api/files/{file_id}/", response_model=schema.File)
def get_file_details(file_id: int, db: Session = Depends(get_db)) -> Any:
    """Get detail for a given file_id"""
    file = workers.get_file(db, file_id)
    return file


@app.get("/api/files/", response_model=List[schema.File])
def get_files(db: Session = Depends(get_db)) -> Any:
    """Get all files in the database"""
    files = workers.get_files(db)
    return files


@app.get("/api/files/{file_id}/{model}/", response_model=schema.File)
def get_file_prediction_filtered_by_model(
    file_id: int, model: str, db: Session = Depends(get_db)
) -> Any:
    """Get file prediction filtered by model"""
    file = workers.get_file_prediction_filtered_by_model(db, file_id, model)
    return file
