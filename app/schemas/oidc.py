from pydantic import BaseModel, EmailStr


class OIDCAuthorize(BaseModel):
    email: EmailStr
    password: str
    response_type: str
    client_id: str
    redirect_uri: str
    scope: str
    state: str