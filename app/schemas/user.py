import enum
from typing import Optional

from pydantic import BaseModel, UUID4, EmailStr


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    password: str
    email: EmailStr
    phone_number: Optional[str] = ''

    class Config:
        from_attributes = True


class UserOut(BaseModel):
    id: UUID4
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: Optional[str] = ''
    email_verified: bool
    phone_number_verified: bool

    class Config:
        from_attributes = True


class Rule(enum.Enum):
    DELETE = 'delete'
    UPDATE = 'update'
    SUPER = 'super'

