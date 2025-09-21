from sqlalchemy import Column, Integer, String

from src.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    def __init__(
        self,
        name: str,
    ) -> None:
        self.name = name
