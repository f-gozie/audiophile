from typing import Any, List
from functools import lru_cache

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import Depends, FastAPI, HTTPException, File, UploadFile
from sqlalchemy.orm import Session

from audiophile.config.database import SessionLocal, engine

from . import models, schema, workers
from .schema import Prediction
from .tasks import generate_predictions
from .utils.constants import (MODEL_CONFIDENCE_THRESHOLD, MODEL_DICT,
                              SAMPLE_RATE)
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
    scheduler.add_job(generate_predictions, "interval", [settings.BASE_URL], minutes=2)
    scheduler.start()


@app.post("/api/files/upload")
def create_file(file: UploadFile = File(...)):
    """Create a new file in the database
    Args:
        file: The file to be uploaded
    Returns:
        A success message if file was uploaded successfully
    """
    response = workers.upload_file(file, settings.FILE_PATH)
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


@app.get("/api/detect/{utterance}/{audio_loc}", response_model=List[Prediction])
def generate_phrase_detections(utterance: str, audio_loc: str) -> Any:
    """Run inference on an audio file with a model for an utterance. Currently
    available utterances are: "call", "is", "recorded"

    Args:
        utterance: Case sensitive name of the model to be used for inference
        audio_loc: The full or relative path to the audio file for which inference
            is to be executed
    """
    try:
        model = MODEL_DICT[utterance]
    except KeyError:
        raise HTTPException(
            404, f"Utterance {utterance} not found in local model dictionary"
        )

    try:
        resampled_audio = load_resampled(audio_loc, SAMPLE_RATE)
    except FileNotFoundError:
        raise HTTPException(404, f"File {audio_loc} not found")

    predictions = []
    for time, audio_snip in iterate_call(resampled_audio):
        confidence = model(audio_snip)
        if confidence > MODEL_CONFIDENCE_THRESHOLD:
            predictions.append(
                Prediction(
                    utterance=utterance, time=time / SAMPLE_RATE, confidence=confidence
                )
            )

    return predictions
