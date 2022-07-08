import torch


class InferenceModel:
    """A mocked model class that gives random predictions"""

    def __call__(self, audio: torch.tensor) -> float:
        """A random prediction method that predicts float values between 0 and 1

        Args:
            audio: Tensor representation of the audio file

        Returns:
            Float value representing the confidence of the prediction
        """
        return float(torch.rand(1))


MODEL_CONFIDENCE_THRESHOLD = 0.9
SAMPLE_RATE = 8000
MODEL_DICT = {
    "call": InferenceModel(),
    "is": InferenceModel(),
    "recorded": InferenceModel(),
}
