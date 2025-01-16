from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.base import NPIException
from app.exceptions.repository import DeleteException
from app.models.oauth2_client import OAuth2Client
from app.repositories.repository import Repository


class OAuth2ClientRepository(Repository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, client: OAuth2Client):
        try:
            self.session.add(client)
            await self.session.commit()
            await self.session.refresh(client)
            return client
        except:
            await self.session.rollback()
            raise

    async def get_all(self):
        stmt = select(OAuth2Client)
        result = await self.session.execute(stmt)
        return result.unique().scalars()

    async def get_by_id(self, client_id: UUID | str):
        stmt = select(OAuth2Client).where(OAuth2Client.client_id == client_id)
        result = await self.session.execute(stmt)
        return result.unique().scalars().first()

    async def delete_by_id(self, client_id: str):
        stmt = delete(OAuth2Client).where(OAuth2Client.id == client_id).returning(OAuth2Client)
        try:
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.scalars().first()
        except SQLAlchemyError as e:
            print(e)
            await self.session.rollback()
            raise DeleteException('Deletion failed')

    async def delete_by_client_id(self, client_id: str):
        stmt = delete(OAuth2Client).where(OAuth2Client.client_id == client_id).returning(OAuth2Client)
        try:
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.scalars().first()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise DeleteException('Deletion failed')

    async def get_by_redirect_uri(self, redirect_uri: str):
        stmt = select(OAuth2Client).where(OAuth2Client.redirect_uri == redirect_uri)
        result = await self.session.execute(stmt)
        return result.unique().scalars().first()

    async def update(self, obj):
        pass