import importlib
import inspect

import torch


class InferenceModelV1:
    """A mocked model class that gives random predictions"""

    def __call__(self, audio: torch.tensor) -> float:
        """A random prediction method that predicts float values between 0 and 1

        Args:
            audio: Tensor representation of the audio file

        Returns:
            Float value representing the confidence of the prediction
        """
        return float(torch.rand(1))


class InferenceModelV2:
    """A mocked model class that gives random predictions"""

    def __call__(self, audio: torch.tensor) -> float:
        """A random prediction method that predicts float values between 0 and 1

        Args:
            audio: Tensor representation of the audio file

        Returns:
            Float value representing the confidence of the prediction
        """
        return float(torch.rand(1))


inference_models = []
for name, cls in inspect.getmembers(
    importlib.import_module("audiophile.datasets.models"), inspect.isclass
):
    inference_models.append(cls())
