from typing import Any, List

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import Depends, FastAPI, HTTPException, File, UploadFile
from sqlalchemy.orm import Session

from audiophile.config.database import SessionLocal, engine

from . import models, schema, workers
from .schema import Prediction
from .services.buckets import S3Service
from .tasks import generate_predictions
from .utils.constants import MODEL_CONFIDENCE_THRESHOLD, SAMPLE_RATE, inference_models, keywords
from .utils.helpers import iterate_call, load_resampled
from .config.configuration import settings

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
    scheduler.add_job(generate_predictions, "interval", [settings.BASE_URL], hours=5)
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


@app.get("/api/detect/{utterance}/{audio_loc}", response_model=List[Prediction])
def generate_phrase_detections(utterance: str, audio_loc: str) -> Any:
    """Run inference on an audio file with a model for an utterance. Currently
    available utterances are: "call", "is", "recorded"

    Args:
        utterance: Case sensitive name of the model to be used for inference
        audio_loc: The full or relative path to the audio file for which inference
            is to be executed
    """
    if utterance not in keywords:
        raise HTTPException(
            404, f"Utterance {utterance} not found in local model dictionary"
        )

    try:
        resampled_audio = load_resampled(audio_loc, SAMPLE_RATE)
    except FileNotFoundError:
        raise HTTPException(404, f"File {audio_loc} not found")

    predictions = []
    for time, audio_snip in iterate_call(resampled_audio):
        for model in inference_models:
            model_name = model.__class__.__name__
            confidence = model(audio_snip)
            if confidence > MODEL_CONFIDENCE_THRESHOLD:
                predictions.append(
                    Prediction(
                        utterance=utterance,
                        time=time / SAMPLE_RATE,
                        confidence=confidence,
                        model=model_name
                    )
                )

    return predictions
