import os

from audiophile import workers
from audiophile.config.database import SessionLocal
from audiophile.utils import helpers
from audiophile.utils.constants import keywords as phrases


def generate_predictions(base_url):
    with SessionLocal() as db:
        audio_files_path = f"{os.getcwd()}/utils/media/"
        for root, dirs, files in os.walk(audio_files_path):
            for file in files:
                if file.endswith(".wav"):
                    file_path = os.path.join(root, file)
                    file_name = file.split(".")[0]
                    file_duration = helpers.get_file_duration(file_path)
                    file_obj, _ = workers.get_or_create_file(
                        file=file_name, duration=file_duration, db=db
                    )
                    reference = helpers.generate_unique_reference_id()
                    for phrase in phrases:
                        file_predictions = helpers.get_file_predictions(
                            base_url, phrase, file
                        )
                        for prediction in file_predictions:
                            prediction["reference"] = reference
                            workers.create_prediction(
                                db=db, file_id=file_obj.id, **prediction
                            )
                    workers.update_file(db=db, file_id=file_obj.id, reference=reference)
