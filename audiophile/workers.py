from sqlalchemy.orm import Session

from . import models, schema


def get_file_predictions(
    db: Session, file_id: int, skip: int = 0, limit: int = 100
) -> schema.File:
    """Get all predictions for a given file_id

    Args:
        db: SQLAlchemy session object
        file_id: The id of the file for which predictions are to be retrieved
        skip: The number of predictions to skip
        limit: The max number of predictions to return in a single call

    Returns:
        A list of predictions for the given file_id
    """
    predictions = (
        db.query(models.File)
        .filter(models.File.id == file_id)
        .first()
        .predictions  # noqa: E501
    )
    return predictions
