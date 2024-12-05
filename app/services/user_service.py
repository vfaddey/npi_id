from uuid import UUID

from pydantic import EmailStr

from app.core.jwt_provider import JWTProvider
from app.core.security import verify_password, hash_password
from app.exceptions.token import InvalidTokenException
from app.exceptions.user import UserNotFoundException, AuthenticationException, AuthorizationException, \
    UserAlreadyExistsException
from app.models.user import User
from app.schemas.token import Token, FullToken
from app.schemas.user import UserCreate, UserOut
from jose import JWTError


class UserService:
    def __init__(self, repository):
        self.repository = repository

    async def create(self, user: UserCreate) -> UserOut:
        existing_user = await self.repository.get_by_email(user.email)
        if existing_user:
            raise UserAlreadyExistsException('User with such email already exists')
        user_model = User(**user.dict())
        hashed_password = hash_password(user_model.password)
        user_model.password = hashed_password
        inserted_user = await self.repository.add(user_model)
        if not inserted_user:
            raise Exception('Failed to create user')
        token = self.create_token(user_model.id, user_model.email, full_token=True)
        return token

    async def get_by_id(self, user_id: UUID) -> UserOut:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(f'No user with such id: {user_id}')
        return UserOut.from_orm(user)

    async def delete_by_id(self, user_id: UUID) -> UserOut:
        result = await self.repository.delete_by_id(user_id)
        if not result:
            raise UserNotFoundException(f'No user with such id: {user_id}')
        return UserOut.from_orm(result)

    def create_token(self, user_id: UUID, email: EmailStr, full_token=False) -> Token:
        payload = {
            'sub': str(user_id),
            'email': email
        }
        try:
            access_token = JWTProvider.encode_access_token(payload)
            token_type = JWTProvider.token_type
            if full_token:
                refresh_token = JWTProvider.encode_refresh_token(payload)
                return FullToken(access_token=access_token, refresh_token=refresh_token, token_type=token_type)
            return Token(access_token=access_token, token_type=token_type)
        except JWTError as e:
            raise AuthenticationException('Failed to create token')

    async def verify_credentials(self, token: str) -> UserOut:
        try:
            payload = JWTProvider.decode(token)
            user_id = payload.get('sub')
            user = await self.repository.get_by_id(user_id)
            if not user:
                raise UserNotFoundException(f'No user with such id: {user_id}')
            return UserOut.from_orm(user)
        except InvalidTokenException as e:
            raise AuthorizationException(str(e))

    async def refresh_token(self, token: str) -> Token:
        user = await self.verify_credentials(token)
        new_access_token = self.create_token(user.id, user.email)
        return new_access_token

    async def authenticate_user(self, email: str, password: str) -> Token:
        user = await self.authorize_user(email, password)
        return self.create_token(user.id, email, full_token=True)

    async def authorize_user(self, email: str, password: str) -> UserOut:
        user = await self.repository.get_by_email(email)
        if not user:
            raise UserNotFoundException(f'No user with such email: {email}')
        if not verify_password(password, user.password):
            raise AuthenticationException('Incorrect password')
        return UserOut.from_orm(user)
