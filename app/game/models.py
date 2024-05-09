from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.store.database.sqlalchemy_base import BaseModel


class GamesQuestionsTable(BaseModel):
    __tablename__ = "game_question"

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey("games.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))


class GamesUsersTable(BaseModel):
    __tablename__ = "game_user"

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey("games.id"))
    user_id = Column(Integer, ForeignKey("users.id"))


class Game(BaseModel):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(Integer, nullable=False)
    captain = Column(ForeignKey("users.id"))
    players = relationship("UserModel", secondary="game_user")
    finished = Column(String, default="Not finished")
    winner = Column(String, default="No winner")
    players_count = Column(Integer, default=0)
    bot_count = Column(Integer, default=0)
    questions = relationship("QuestionModel", secondary="game_question")
