from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.security import ALGORITHM, SECRET_KEY
from src.database import get_db
from src.redis_client import RedisClientWrapper, get_redis
from src.services.user_service import UserService

# tokenUrl points to the login route for Swagger UI compatibility
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# Dependency to provide the Service Layer
async def get_user_service(
    session: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis)
) -> UserService:
    redis_wrapper = RedisClientWrapper(redis)
    return UserService(session, redis_wrapper)


async def auth_required(
    request: Request,
    token: str = Depends(oauth2_scheme),
    service: UserService = Depends(get_user_service) # Your existing dependency
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        
        # Optimized lookup (Redis -> DB) via Service Layer
        user = await service.get_user_profile(int(user_id_str))
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        # Attach user to request state
        request.state.user = user
        
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )