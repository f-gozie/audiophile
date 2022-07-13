import json
import uuid
import wave
from typing import Dict, Iterator, List, Tuple

import pandas as pd
import requests
import torch
import torchaudio
from evidently import ColumnMapping
from evidently.model_profile import Profile
from evidently.model_profile.sections import DataDriftProfileSection
from torchaudio import transforms


def load_resampled(audio_loc: str, resample_rate: int = 8000) -> torch.tensor:
    """Load and resample an audio file

    Args:
        audio_loc: Full or relative path to the audio file
        resample_rate: What sampling rate should the audio file be resampled
            to. Defaults to 8000

    Returns:
        torch.tensor with loaded audio file data

    Raises:
        FileNotFoundError: If the audio_loc is not a valid audio file
    """
    try:
        audio, rate = torchaudio.load(f"audiophile/utils/media/{audio_loc}")
    except RuntimeError as e:
        raise FileNotFoundError(e)

    resampler = transforms.Resample(rate, resample_rate)
    return resampler(audio)


def iterate_call(
    audio: torch.tensor, stride: int = 8000, window: int = 8000
) -> Iterator[Tuple[int, torch.tensor]]:
    """Iterate over an audio tensor in with given stride and window

    Args:
        audio: The tensor containing audio file data
        stride: The amount of samples to move at each iteration
        window: The amount of samples to include in the cut audio

    Yields:
        A tuple containing the starting time index of the audio snipet and
            a tensor containing the audio data
    """
    for start in range(audio.shape[-1] // stride):
        start_idx = start * stride
        yield start_idx, audio[:, start_idx : start_idx + window]  # noqa: E203


def get_file_duration(audio_loc: str) -> float:
    """Get the duration of an audio file

    Args:
        audio_loc: Full or relative path to the audio file

    Returns:
        The duration of the audio file in seconds
    """
    with wave.open(audio_loc, "rb") as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
        return duration


def get_file_predictions(base_url: str, phrase: str, audio_loc: str) -> List[Dict]:
    """Get the predictions for an audio file from predictions endpoint

    Args:
        base_url: The base url of the predictions endpoint
        phrase: The phrase to be used for inference
        audio_loc: Full or relative path to the audio file

    Returns:
        A list of predictions
    """
    phrase_detection_path = f"/api/detect/{phrase}/{audio_loc}"
    response = requests.get(base_url + phrase_detection_path)
    return response.json()


def generate_unique_reference_id() -> str:
    """Generate a unique reference id

    Returns:
        A unique reference id
    """
    return str(uuid.uuid4())


def does_data_drift_exist(existing_data: pd.DataFrame, new_data: List[Dict]) -> bool:
    """Check if the predictions are within the duration of the audio file

    Args:
        existing_data: Data to compare against
        new_data: New data to be compared

    Returns:
        True if the current data is corrupted and would cause data drift, else False
    """
    existing_data = existing_data.drop(["id", "file_id", "reference"], axis=1)
    column_map = ColumnMapping(target="confidence")
    new_data = pd.DataFrame.from_records(new_data)

    drift_profile = Profile(sections=[DataDriftProfileSection()])
    drift_profile.calculate(existing_data, new_data, column_map)
    drift_data = dict(json.loads(drift_profile.json()))
    if drift_data["data_drift"]["data"]["metrics"]["confidence"]["drift_detected"]:
        return True
    return False
