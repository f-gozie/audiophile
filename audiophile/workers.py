from typing import List, Tuple

from fastapi import HTTPException
from sqlalchemy.orm import Session

from . import models, schema


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
    file = db.query(models.File).filter_by(**kwargs).first()
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
) -> int:
    """Create a new prediction in the database

    Args:
        db: SQLAlchemy session object
        file_id: The id of the file for which the prediction is to be created
        utterance: The phrase detected in the audio file
        confidence: The confidence of the prediction to be created
        time: The time at which the phrase was detected
        reference: The reference used to get the latest predictions

    Returns:
        The id of the newly created prediction
    """
    prediction = models.Prediction(
        file_id=file_id,
        utterance=utterance,
        confidence=confidence,
        time=time,
        reference=reference,
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return prediction.id
