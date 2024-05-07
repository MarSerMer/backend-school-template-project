from dataclasses import dataclass

from sqlalchemy import Column, ForeignKey, Integer, String

from app.store.database.sqlalchemy_base import BaseModel


@dataclass
class Answer:
    body: str


@dataclass
class Question:
    id: int
    question: str


class QuestionModel(BaseModel):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(String, nullable=False)


class AnswerModel(BaseModel):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    answer = Column(String, nullable=False)
    question_id = Column(ForeignKey("questions.id", ondelete="CASCADE"),
                         nullable=False)
