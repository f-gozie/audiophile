from typing import List, Tuple

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from . import models, schema
from .services.buckets import S3Service
from .utils.constants import MODEL_CONFIDENCE_THRESHOLD, SAMPLE_RATE, inference_models, keywords
from .utils.helpers import iterate_call, load_resampled


async def upload_file_to_s3(file: UploadFile, s3_client: S3Service):
    """Upload a file to s3 bucket

    Args:
        file: The file blob to be uploaded
        s3_client: The s3 client for making requests to the s3 bucket

    Returns:
        The id of the uploaded file
    """
    file_bytes_obj = file.file.read()
    await s3_client.upload_file(file_bytes_obj, file)


def upload_file_to_local(file: UploadFile, file_path: str):
    """Upload a file to local disk

    Args:
        file: The file blob to be uploaded
        file_path: The path to the file to be uploaded

    Returns:
        The id of the uploaded file
    """
    file_bytes_obj = file.file.read()
    file_location = f"{file_path}/{file.filename}"
    with open(file_location, "wb+") as f:
        f.write(file_bytes_obj)
    return {"message": f"File {file.filename} uploaded successfully"}


def get_file(db: Session, file_id: int) -> schema.File:
    """Get all details for a given file_id

    Args:
        db: SQLAlchemy session object
        file_id: The id of the file for which predictions are to be retrieved

    Returns:
        An object containing data for the given file_id
    """
    file = db.query(models.File).filter(models.File.id == file_id).first()
    if not file:
        raise HTTPException(404, f"File with id {file_id} not found in database")
    file.confidences = file.confidences_filtered(file.reference)
    return file


def get_file_prediction_filtered_by_model(
    db: Session, file_id: int, model: str
) -> schema.File:
    """Get all files in the database filtered by model

    Args:
        db: SQLAlchemy session object
        file_id: The id of the file for which predictions are to be retrieved
        model: The model for which to filter the files

    Returns:
        A file detail containing predictions for a particular file filtered by the model
    """
    allowed_models = [model.__class__.__name__ for model in inference_models]
    if model not in allowed_models:
        raise HTTPException(400, f"Model {model} not supported")
    file = db.query(models.File).filter(models.File.id == file_id).first()
    if not file:
        raise HTTPException(404, f"File with id {file_id} not found in database")
    file.confidences = file.confidences_filtered_by_model(model)
    return file


def get_files(db: Session) -> List[schema.File]:
    """Get all files in the database

    Args:
        db: SQLAlchemy session object

    Returns:
        A list of objects containing data for all files in the database
    """
    files = db.query(models.File).all()
    return files


def create_file(db: Session, file_name: str, file_duration: int) -> int:
    """Create a new file in the database

    Args:
        db: SQLAlchemy session object
        file_name: The name of the file to be created
        file_duration: The duration of the file to be created

    Returns:
        The id of the newly created file
    """
    file = models.File(file=file_name, duration=file_duration)
    db.add(file)
    db.commit()
    db.refresh(file)
    return file.id


def update_file(db: Session, file_id: int, **kwargs) -> int:
    """Update a file in the database

    Args:
        db: SQLAlchemy session object
        file_id: The id of the file to be updated
        kwargs: The keyword arguments to be used to update the file

    Returns:
        The id of the updated file
    """
    file = db.query(models.File).filter(models.File.id == file_id).first()
    if not file:
        raise HTTPException(404, f"File with id {file_id} not found in database")
    for key, value in kwargs.items():
        setattr(file, key, value)
    db.commit()
    db.refresh(file)
    return file.id


def get_or_create_file(db: Session, **kwargs) -> Tuple[models.File, bool]:
    """Get or create a file in the database

    Args:
        db: SQLAlchemy session object
        kwargs: The keyword arguments to be used to create a new file

    Returns:
        The id of the newly created file
    """
    file = (
        db.query(models.File)
        .filter(
            models.File.file == kwargs["file"]
            and models.File.duration == kwargs["duration"]
        )
        .first()
    )
    created = False
    if not file:
        file = models.File(**kwargs)
        db.add(file)
        db.commit()
        db.refresh(file)
        created = True
    return file, created


def create_prediction(
    db: Session,
    file_id: int,
    utterance: str,
    confidence: float,
    time: int,
    reference: str,
    model: str,
) -> int:
    """Create a new prediction in the database

    Args:
        db: SQLAlchemy session object
        file_id: The id of the file for which the prediction is to be created
        utterance: The phrase detected in the audio file
        confidence: The confidence of the prediction to be created
        time: The time at which the phrase was detected
        reference: The reference used to get the latest predictions
        model: The model the inference was run on

    Returns:
        The id of the newly created prediction
    """
    prediction = models.Prediction(
        file_id=file_id,
        utterance=utterance,
        confidence=confidence,
        time=time,
        reference=reference,
        model=model,
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return prediction.id


def generate_phrase_detections(
    utterance: str, audio_loc: str
) -> List[models.Prediction]:
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
                    schema.Prediction(
                        utterance=utterance,
                        time=time / SAMPLE_RATE,
                        confidence=confidence,
                        model=model_name,
                    )
                )

    return predictions
