from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from app.api.deps import get_user_service
from app.exceptions.base import NPIException
from app.schemas.token import Token, RefreshTokenRequest
from app.schemas.user import UserCreate
from app.services.user_service import UserService

router = APIRouter(tags=['Auth'])


@router.post('/refresh')
async def refresh_access_token(request: RefreshTokenRequest,
                               user_service: UserService = Depends(get_user_service)):
    try:
        return await user_service.refresh_token(request.refresh_token)
    except NPIException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post('/login')
async def login(form_data: OAuth2PasswordRequestForm = Depends(),
                user_service: UserService = Depends(get_user_service)):
    email = form_data.username
    password = form_data.password
    try:
        token = await user_service.authenticate_user(email, password)
        return token
    except NPIException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post('/register', response_model=Token)
async def register(add_user: UserCreate,
                   user_service: UserService = Depends(get_user_service)):
    try:
        token = await user_service.create(add_user)
        return token
    except NPIException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post('/forgot')
async def forgot_password():
    ...
