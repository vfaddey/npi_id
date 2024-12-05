from typing import List

from app.exceptions.oauth2_client import ClientNotFound, ClientAlreadyExists
from app.exceptions.repository import DeleteException
from app.models.oauth2_client import OAuth2Client
from app.schemas.oauth2_client import OAuth2ClientOut
from app.repositories.oauth2_repository import OAuth2ClientRepository
import secrets

from app.schemas.oauth2_client import OAuth2ClientCreate


class OAuth2ClientService:
    def __init__(self, repository: OAuth2ClientRepository):
        self.repository = repository

    async def create(self, client: OAuth2ClientCreate) -> OAuth2ClientOut:
        try:
            client_id = secrets.token_urlsafe(24)
            client_secret = secrets.token_urlsafe(48)
            client_data = client.dict()
            client_data['redirect_uri'] = str(client.redirect_uri)
            if await self.__check_if_exists(client_data['redirect_uri']):
                raise ClientAlreadyExists(f'Client with redirect_uri {client_data["redirect_uri"]} already exists.')
            client_model = OAuth2Client(
                client_id=client_id,
                client_secret=client_secret,
                **client_data
            )
            inserted_client = await self.repository.add(client_model)
            return OAuth2ClientOut.from_orm(inserted_client)
        except:
            raise

    async def get_all(self) -> List[OAuth2ClientOut]:
        result = await self.repository.get_all()
        return [OAuth2ClientOut.from_orm(c) for c in result]

    async def delete_by_client_id(self, client_id: str) -> OAuth2ClientOut:
        try:
            client = await self.repository.delete_by_client_id(client_id)
            if not client:
                raise ClientNotFound(f'Client with client_id {client_id} not found')
            return OAuth2ClientOut.from_orm(client)
        except DeleteException as e:
            raise ClientNotFound(f'Something went wrong while deleting client with client_id {client_id}')

    async def get_by_client_id(self, client_id: str) -> OAuth2ClientOut:
        client = await self.repository.get_by_id(client_id)
        if not client:
            raise ClientNotFound(f'Client with client_id {client_id} not found')
        return client

    async def __check_if_exists(self, redirect_uri: str) -> bool:
        result =  await self.repository.get_by_redirect_uri(redirect_uri)
        if result:
            return True
        return False