from typing import List

from pydantic import BaseModel


class Prediction(BaseModel):
    utterance: str
    time: int
    confidence: float
    reference: str = ""

    class Config:
        orm_mode = True


class File(BaseModel):
    file: str
    duration: int
    reference: str
    confidences: List[Prediction]

    class Config:
        orm_mode = True
