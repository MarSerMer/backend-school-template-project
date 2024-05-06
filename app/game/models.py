from dataclasses import dataclass

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Table
from sqlalchemy.orm import relationship

from app.store.database.sqlalchemy_base import BaseModel

game_question_table = Table (
    "game_question",
    BaseModel.metadata,
    Column("id", primary_key=True),
    Column("game", ForeignKey("games.id")),
    Column("question", ForeignKey("questions.id"))
)

game_users_table = Table (
    "game_user",
BaseModel.metadata,
    Column("id", primary_key=True),
    Column("game", ForeignKey("games.id")),
    Column("user", ForeignKey("users.id"))
)

class Game(BaseModel):
    __tablename__= "games"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(Integer, nullable=False)
    captain = Column(ForeignKey("users.id"))
    players = relationship(secondary=game_users_table, back_populates="user")
    finished = Column(String, default="Not finished")
    winner = Column(String, default="No winner")
    players_count = Column(Integer, default=0)
    bot_count = Column(Integer, default=0)
    questions = relationship(secondary=game_question_table, back_populates="question")