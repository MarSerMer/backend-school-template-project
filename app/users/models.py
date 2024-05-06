from dataclasses import dataclass

from sqlalchemy import Column, Integer, String

from app.store.database.sqlalchemy_base import BaseModel

@dataclass
class User:
    id: int
    vk_id: int
    first_name: str
    last_name: str

class UserModel(BaseModel):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    vk_id = Column(Integer, nullable=False)
    first_name = Column(String)
    last_name = Column(String)