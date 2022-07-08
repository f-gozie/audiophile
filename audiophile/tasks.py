import datetime
import os

from audiophile import models, workers
from audiophile.config.database import SessionLocal
from audiophile.utils import helpers
from audiophile.utils.constants import MODEL_DICT


def generate_predictions(base_url):
    with SessionLocal() as db:
        audio_files_path = f"{os.getcwd()}/audiophile/utils/media/"
        for root, dirs, files in os.walk(audio_files_path):
            for file in files:
                pass
                if file.endswith(".wav"):
                    file_path = os.path.join(root, file)
                    file_name = file.split(".")[0]
                    file_duration = helpers.get_file_duration(file_path)
                    file_id, created = workers.get_or_create_file(
                        file=file_name, duration=file_duration, db=db
                    )
                    phrases = MODEL_DICT.keys()
                    for phrase in phrases:
                        file_predictions = helpers.get_file_predictions(
                            base_url, phrase, file
                        )
                        for prediction in file_predictions:
                            workers.create_prediction(
                                db=db, file_id=file_id, **prediction
                            )
        print(f"The time is executing. Current time is {datetime.datetime.now()}")
        files = db.query(models.File).all()
    return None
