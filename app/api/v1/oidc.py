from typing import List

from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader, select_autoescape
from starlette import status
from starlette.responses import RedirectResponse

from app.api.deps import get_oath2_client_service, get_current_admin, get_user_service, get_current_user
from app.core.jwt_provider import JWTProvider
from app.exceptions.base import NPIException
from app.exceptions.oauth2_client import ClientNotFound, ClientAlreadyExists
from app.schemas.oauth2_client import OAuth2ClientCreate, OAuth2ClientOut
from app.schemas.oidc import OIDCAuthorize
from app.schemas.token import FullToken
from app.schemas.user import UserOut
from app.services.oauth2_service import OAuth2ClientService
from app.services.user_service import UserService

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



@router.get('/.well-known/openid-configuration')
async def get_configuration():
    return {

    }

@router.get('/authorize')
async def authorize_get(
    response_type: str,
    client_id: str,
    redirect_uri: str,
    scope: str,
    state: str,
):
    template = env.get_template("login.html")
    return HTMLResponse(template.render(response_type=response_type, client_id=client_id, redirect_uri=redirect_uri, scope=scope, state=state, error=None))


@router.post('/authorize')
async def authorize(
    authorize_schema: OIDCAuthorize,
    client_service: OAuth2ClientService = Depends(get_oath2_client_service),
    user_service: UserService = Depends(get_user_service)
):
    user_email = authorize_schema.email
    user_password = authorize_schema.password
    try:
        user = await user_service.authorize_user(user_email, user_password)
    except NPIException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    try:
        client = await client_service.get_by_client_id(authorize_schema.client_id)
    except ClientNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    if str(client.redirect_uri) not in authorize_schema.redirect_uri:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='Redirect URI is invalid')
    if authorize_schema.response_type != client.response_type:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='Response type is invalid')
    if authorize_schema.scope != client.scope:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='Scope is invalid')

    payload = {
        "client_id": authorize_schema.client_id,
        "redirect_uri": authorize_schema.redirect_uri,
        "scope": authorize_schema.scope,
        "sub": str(user.id),
    }
    code = JWTProvider.encode_access_token(payload, expires_delta=10)
    redirect_uri = f'{client.redirect_uri}?code={code}&state={authorize_schema.state}'
    return RedirectResponse(redirect_uri, status_code=status.HTTP_302_FOUND)

@router.post('/token', response_model=FullToken)
async def get_token(
    grant_type: str = Form(...),
    code: str = Form(None),
    redirect_uri: str = Form(None),
    client_id: str = Form(None),
    client_secret: str = Form(None),
    client_service: OAuth2ClientService = Depends(get_oath2_client_service),
    user_service: UserService = Depends(get_user_service)
):
    try:
        client = await client_service.get_by_client_id(client_id)
    except ClientNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    if client.client_secret != client_secret:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='Client secret is invalid')
    # if client.redirect_uri != redirect_uri:
    #     raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='Redirect URI is invalid')
    # if client.grant_type != grant_type:
    #     raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='Grant type is invalid')

    user = await get_current_user(code, user_service)
    full_token = user_service.create_token(user.id, user.email, full_token=True)
    return full_token

@router.get('/userinfo')
async def userinfo(user: UserOut = Depends(get_current_user)):
    return user


@router.get('/jwks')
async def jwks():
    ...