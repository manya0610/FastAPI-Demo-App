from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.app.routers.deps import get_user_service
from src.auth.security import create_access_token
from src.services.user_service import UserService

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: UserService = Depends(get_user_service),
):
    # This service method should verify password hash
    user = await service.authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    # Create token based on user_id
    token = create_access_token(user_id=user.id)

    return {"access_token": token, "token_type": "bearer"}
