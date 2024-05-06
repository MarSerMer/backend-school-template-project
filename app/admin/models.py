from dataclasses import dataclass

from sqlalchemy import Column, Integer, String

from app.store.database.sqlalchemy_base import BaseModel

from typing import Optional
from hashlib import sha256


class AdminModel(BaseModel):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)


@dataclass
class Admin:
    id: int
    email: str
    password: Optional[str] = None

    @staticmethod
    def hash_password(password: str) -> str:
        return sha256(password.encode()).hexdigest()

    def password_ok(self, password: str) -> bool:
        return self.hash_password(password) == self.password

    @classmethod
    def admin_from_session(cls, session: Optional[dict]) -> Optional["Admin"]:
        return cls(id=session["admin"]["id"], email=session["admin"]["email"])
