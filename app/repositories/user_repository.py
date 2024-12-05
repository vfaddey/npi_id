from sqlalchemy import select, delete
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.repository import Repository


class UserRepository(Repository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, user: User):
        try:
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            return user
        except:
            await self.session.rollback()
            raise

    async def get_by_id(self, user_id: UUID):
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.unique().scalars().first()

    async def get_by_email(self, email: str):
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.unique().scalars().first()

    async def delete_by_id(self, user_id: int):
        stmt = delete(User).where(User.id == user_id).returning(User)
        try:
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.scalars().first()
        except:
            await self.session.rollback()
            raise

    async def update(self, user: User):
        try:
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            return user
        except:
            await self.session.rollback()
            raise