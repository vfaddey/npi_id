from typing import List

from fastapi import APIRouter, Depends, HTTPException
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy.util import await_only
from starlette import status

from app.api.deps import get_oath2_client_service, get_current_admin
from app.exceptions.base import NPIException
from app.exceptions.oauth2_client import ClientNotFound, ClientAlreadyExists
from app.schemas.oauth2_client import OAuth2ClientCreate, OAuth2ClientOut
from app.services.oauth2_service import OAuth2ClientService

router = APIRouter(prefix="/oidc", tags=["oidc"])

env = Environment(
    loader=FileSystemLoader("app/api/v1/templates"),
    autoescape=select_autoescape(['html', 'xml'])
)


@router.post('/client', response_model=OAuth2ClientOut, dependencies=[Depends(get_current_admin)])
async def create_client(client: OAuth2ClientCreate,
                        client_service: OAuth2ClientService = Depends(get_oath2_client_service)):
    try:
        result = await client_service.create(client)
        return result
    except ClientAlreadyExists as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except NPIException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get('/clients', response_model=List[OAuth2ClientOut], dependencies=[Depends(get_current_admin)])
async def get_clients(client_service: OAuth2ClientService = Depends(get_oath2_client_service)):
    try:
        return await client_service.get_all()
    except NPIException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete('/client/{client_id}', response_model=OAuth2ClientOut, dependencies=[Depends(get_current_admin)])
async def delete_client(client_id: str,
                        client_service: OAuth2ClientService = Depends(get_oath2_client_service)):
    try:
        result = await client_service.delete_by_client_id(client_id)
        return result
    except ClientNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NPIException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get('/authorize')
async def authorize_get(
    response_type: str,
    client_id: str,
    redirect_uri: str,
    scope: str,
    state: str,
):
    template = env.get_template("login.html")
    return template.render(client_id=client_id, redirect_uri=redirect_uri, scope=scope, state=state, error=None)


@router.post('/authorize')
async def authorize(
    response_type: str,
    client_id: str,
    redirect_uri: str,
    scope: str,
    state: str,
    client_service: OAuth2ClientService = Depends(get_oath2_client_service),
):
    try:
        client = await client_service.get_by_client_id(client_id)
    except ClientNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    if redirect_uri != client.redirect_uri:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='Redirect URI is invalid')
    if response_type != client.response_type:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='Response type is invalid')


@router.post('/token')
async def token():
    ...


@router.get('/jwks')
async def jwks():
    ...