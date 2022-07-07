from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Text, Time, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func


Base = declarative_base()


class File(Base):
    __tablename__ = "file"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    duration = Column(Time, default=func.now())

    def __repr__(self):
        return f"<File(name='{self.name}', duration='{self.duration}')>"


class Prediction(Base):
    __tablename__ = 'prediction'
    id = Column(Integer, primary_key=True)
    phrase = Column(String)
    time_stamp = Column(Time)
    confidence = Column(Float)
    created_at = Column(DateTime, default=func.now())
    file_id = Column(Integer, ForeignKey('files.id'))
    file = relationship(File)

    def __repr__(self):
        return '<Predictions %r>' % self.prediction
