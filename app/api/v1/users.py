from fastapi import APIRouter
from fastapi.params import Depends

from app.api.deps import get_current_user
from app.schemas.user import UserOut

router = APIRouter(prefix='/users', tags=['Users'])


@router.get('/me', response_model=UserOut)
async def get_me(user: UserOut = Depends(get_current_user)):
    return user
