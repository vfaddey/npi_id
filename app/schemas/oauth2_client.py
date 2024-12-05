from typing import Optional

from pydantic import BaseModel, HttpUrl, field_validator


class OAuth2ClientCreate(BaseModel):
    redirect_uri: HttpUrl
    scope: Optional[str] = 'openid profile email'
    response_type: Optional[str] = 'code'
    grant_type: Optional[str] = 'authorization_code'


class OAuth2ClientOut(OAuth2ClientCreate):
    client_id: str
    client_secret: str

    class Config:
        from_attributes = True
