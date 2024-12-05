from fastapi import HTTPException
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.db.database import AsyncSessionFactory
from app.exceptions.admin import NotAllowedException
from app.exceptions.user import AuthorizationException
from app.repositories.oauth2_repository import OAuth2ClientRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserOut
from app.services.admin_service import AdminService
from app.services.oauth2_service import OAuth2ClientService
from app.services.user_service import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login')


async def get_session() -> AsyncSession:
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_user_service(session: AsyncSession = Depends(get_session)):
    repository = UserRepository(session)
    return UserService(repository)

async def get_admin_service(session: AsyncSession = Depends(get_session)):
    repository = UserRepository(session)
    return AdminService(repository)

async def get_oath2_client_service(session: AsyncSession = Depends(get_session)):
    repository = OAuth2ClientRepository(session)
    return OAuth2ClientService(repository)


async def get_current_user(token: str = Depends(oauth2_scheme),
                           user_service: UserService = Depends(get_user_service)) -> UserOut:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        return await user_service.verify_credentials(token)
    except AuthorizationException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except:
        raise credentials_exception


async def get_current_admin(token: str = Depends(oauth2_scheme),
                            admin_service: AdminService = Depends(get_user_service)) -> UserOut:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        return await admin_service.verify_credentials(token)
    except AuthorizationException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except NotAllowedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except:
        raise credentials_exception