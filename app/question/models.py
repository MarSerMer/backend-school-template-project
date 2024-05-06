from dataclasses import dataclass

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.store.database.sqlalchemy_base import BaseModel


@dataclass
class Answer:
    body: str


@dataclass
class Question:
    id: int
    question: str
    theme_id: int
    answers: list[Answer]


class QuestionModel(BaseModel):
    __tablaname__ = "questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(String, nullable=False)
    answers = relationship("AnswerModel", back_populates="question")



class AnswerModel(BaseModel):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    answer = Column(String, nullable=False)
    question_id = Column(ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    question = relationship("QuestionModel", back_populates="answers")