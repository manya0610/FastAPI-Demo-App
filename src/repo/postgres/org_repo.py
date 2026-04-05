from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Org
from src.repo.postgres.base_repo import BaseRepository


class OrgRepository(BaseRepository[Org]):
    def __init__(self, session: AsyncSession) -> "OrgRepository":
        super().__init__(Org, session)
