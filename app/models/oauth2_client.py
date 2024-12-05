import datetime
import uuid

from sqlalchemy import Column, String, DateTime, UUID

from app.db.database import Base


class OAuth2Client(Base):
    __tablename__ = 'oauth2_clients'

    id = Column(UUID, default=uuid.uuid4, primary_key=True)
    client_id = Column(String(48), unique=True, index=True, nullable=False)
    client_secret = Column(String(120), nullable=False)
    redirect_uri = Column(String, nullable=False)
    scope = Column(String, default='openid profile email')
    grant_type = Column(String, default='authorization_code')
    response_type = Column(String, default='code')
    token_endpoint_auth_method = Column(String, default='client_secret_basic')
    created_at = Column(DateTime, default=datetime.datetime.utcnow)