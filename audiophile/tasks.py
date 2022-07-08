import datetime

from audiophile import models
from audiophile.database import SessionLocal

# import requests


def generate_predictions():
    with SessionLocal() as db:
        with db.begin():
            print(f"The time is executing. Current time is {datetime.datetime.now()}")
            files = db.query(models.File).all()
            print(files)
    return None
