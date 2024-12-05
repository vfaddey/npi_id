from uuid import UUID

from app.core.jwt_provider import JWTProvider
from app.exceptions.admin import NotAllowedException
from app.exceptions.token import InvalidTokenException
from app.exceptions.user import UserNotFoundException, AuthorizationException
from app.schemas.user import UserOut


class AdminService:
    def __init__(self, repository):
        self.repository = repository

    async def delete_by_id(self, user_id: UUID) -> UserOut:
        result = await self.repository.delete_by_id(user_id)
        if not result:
            raise UserNotFoundException(f'No user with such id: {user_id}')
        return UserOut.from_orm(result)

    async def verify_credentials(self, token: str) -> UserOut:
        try:
            payload = JWTProvider.decode(token)
            user_id = payload.get('sub')
            user = await self.repository.get_by_id(user_id)
            if not user:
                raise UserNotFoundException(f'No user with such id: {user_id}')
            if not user.admin:
                raise NotAllowedException('You are not admin')
            return UserOut.from_orm(user)
        except InvalidTokenException as e:
            raise AuthorizationException(str(e))