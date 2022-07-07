from sqlalchemy import (Column, DateTime, Float, ForeignKey, Integer, String,
                        Time)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class File(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    duration = Column(Time, default=func.now())
    predictions = relationship("Prediction", back_populates="file")

    def __repr__(self):
        return f"<File(name='{self.name}', duration='{self.duration}')>"


class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True)
    phrase = Column(String)
    time = Column(Time)
    confidence = Column(Float)
    created_at = Column(DateTime, default=func.now())
    file_id = Column(Integer, ForeignKey("files.id"))
    file = relationship("File", back_populates="predictions")

    def __repr__(self):
        return "<Predictions %r>" % self.prediction
