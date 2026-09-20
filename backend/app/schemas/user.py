from typing import Optional
from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: Optional[str] = ""


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None


class UserRoleUpdate(BaseModel):
    role: str


class PasswordChange(BaseModel):
    old_password: str
    new_password: str


class UserResponse(BaseModel):
    uid: str
    name: str
    email: str
    phone: Optional[str] = ""
    role: Optional[str] = None
    points: int = 0
    deliveries: int = 0

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
