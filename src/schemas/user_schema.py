from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    name: str


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")
    id: int
    name: str


class UserUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    name: str
