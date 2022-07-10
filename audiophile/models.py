from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import object_session, relationship
from sqlalchemy.sql import func

from audiophile.config.database import Base


class File(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True)
    file = Column(String, unique=True)
    duration = Column(Integer)
    confidences = relationship(
        "Prediction", backref="files", lazy=True, cascade="all, delete-orphan"
    )
    reference = Column(String, unique=True)

    def __repr__(self):
        return f"<File(name='{self.file}', duration='{self.duration}')>"

    def confidences_filtered(self, reference):
        return (
            object_session(self)
            .query(Prediction)
            .with_parent(self)
            .filter(Prediction.reference == reference)
            .all()
        )

    def confidences_filtered_by_model(self, model):
        return (
            object_session(self)
            .query(Prediction)
            .with_parent(self)
            .filter(Prediction.model == model)
            .all()
        )


class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True)
    utterance = Column(String)
    time = Column(Integer)
    confidence = Column(Float)
    reference = Column(String)
    model = Column(String)
    created_at = Column(DateTime, default=func.now())
    file_id = Column(Integer, ForeignKey("files.id"))

    def __repr__(self):
        return f"<Prediction(phrase='{self.utterance}', time='{self.time}', confidence='{self.confidence}')>"
