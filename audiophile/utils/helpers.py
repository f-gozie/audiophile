import wave
from typing import Dict, Iterator, List, Tuple

import requests
import torch
import torchaudio
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
