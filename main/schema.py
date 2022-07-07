from pydantic import BaseModel


class Prediction(BaseModel):
    phrase: str
    time: int
    confidence: float
