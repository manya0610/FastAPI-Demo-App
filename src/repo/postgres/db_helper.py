

from sqlalchemy.ext.asyncio import AsyncSession


class UnitOfWork:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def __aenter__(self):  # noqa: D105
        return self

    async def __aexit__(self, exc_type, *args):  # noqa: ANN001, D105
        if exc_type:
            await self.session.rollback()
        else:
            await self.session.commit()