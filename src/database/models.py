from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from src.database import Base


class Org(Base):
    __tablename__ = "orgs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False, index=True)
    config = Column(JSONB, nullable=True)

    users = relationship("User", back_populates="org")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False, index=True)
    password = Column(String, nullable=False)
    org_id = Column(Integer, ForeignKey("orgs.id"), nullable=False, index=True)

    org = relationship("Org", back_populates="users")

    # def __init__(
    #     self,
    #     name: str,
    # ) -> None:
    #     self.name = name
