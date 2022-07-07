from typing import List

from pydantic import BaseModel


class Prediction(BaseModel):
    utterance: str
    time: int
    confidence: float

    class Config:
        orm_mode = True


class File(BaseModel):
    file: str
    duration: int
    confidences: List[Prediction]

    class Config:
        orm_mode = True
