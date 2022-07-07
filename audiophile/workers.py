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
    return file
