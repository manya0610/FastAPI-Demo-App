from contextlib import asynccontextmanager
from src.database import get_db
from src.database.models import User

import asyncio


async def f():
    async_get_db = asynccontextmanager(get_db)
    async with async_get_db() as session:
        user1 = User(name="manish1", password= "1234")
        user2 = User(name="manish2", password= "1234")
        async with session.begin():
            session.add(user1)
            try:
                async with session.begin_nested():
                    session.add(user2)
                    # raise Exception("bbom")
            except Exception as e:
                print(e)
        # return
        # await session.commit()

    return


def main():
    asyncio.run(f())

if __name__ == "__main__":
    main()