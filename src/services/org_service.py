import logging
from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from src.repo.postgres.db_helper import UnitOfWork
from src.repo.postgres.org_repo import OrgRepository
from src.schemas.org_schema import OrgCreate, OrgPublic, OrgUpdate

logger = logging.getLogger(__name__)


class OrgService:
    def __init__(self, session: AsyncSession) -> "OrgService":
        self.repo = OrgRepository(session)
        self.transaction = UnitOfWork(session)

    async def create_org(self, data: OrgCreate) -> OrgPublic:
        async with self.transaction:
            org_model = await self.repo.create(data)
        logger.info("org created, id=%s", org_model.id)
        return OrgPublic.model_validate(org_model)

    async def get_org(self, org_id: int) -> OrgPublic | None:
        org = await self.repo.get(org_id)
        if not org:
            return None
        return OrgPublic.model_validate(org)

    async def list_orgs(self, limit: int = 100, offset: int = 0) -> Sequence[OrgPublic]:
        orgs = await self.repo.list(limit=limit, offset=offset)
        return [OrgPublic.model_validate(o) for o in orgs]

    async def update_org(self, org_id: int, data: OrgUpdate) -> OrgPublic:
        async with self.transaction:
            org_model = await self.repo.update(org_id, data)
        logger.info("org updated, id=%s", org_id)
        return OrgPublic.model_validate(org_model)

    async def remove_org(self, org_id: int) -> bool:
        async with self.transaction:
            success = await self.repo.delete(org_id)
        if success:
            logger.info("org deleted, id=%s", org_id)
        return success
