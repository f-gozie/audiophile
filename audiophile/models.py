from sqlalchemy import (Column, DateTime, Float, ForeignKey, Integer, String,
                        Time)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class File(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True)
    file = Column(String, unique=True)
    duration = Column(Integer)
    confidences = relationship("Prediction", back_populates="file")

    def __repr__(self):
        return f"<File(name='{self.file}', duration='{self.duration}')>"


class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True)
    utterance = Column(String)
    time = Column(Integer)
    confidence = Column(Float)
    created_at = Column(DateTime, default=func.now())
    file_id = Column(Integer, ForeignKey("files.id"))
    file = relationship("File", back_populates="confidences")

    def __repr__(self):
        return f"<Prediction(phrase='{self.phrase}', time='{self.time}', confidence='{self.confidence}')>"
