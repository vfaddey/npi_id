import uuid
from datetime import datetime, timedelta
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import VARCHAR
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    email = Column(VARCHAR(70), unique=True, nullable=False)
    phone_number = Column(VARCHAR(20), nullable=False)
    phone_number_verified = Column(Boolean, nullable=False, default=False)
    email_verified = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    admin = relationship('Admin', back_populates='user')
