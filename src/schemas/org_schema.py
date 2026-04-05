from pydantic import BaseModel, ConfigDict


class OrgCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    name: str
    config: dict | None = None


class OrgPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    id: int
    name: str
    config: dict | None = None


class OrgUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    name: str | None = None
    config: dict | None = None
