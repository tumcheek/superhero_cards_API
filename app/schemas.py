from typing import List

from pydantic import BaseModel, EmailStr


class UserSchema(BaseModel):
    id: int
    email: EmailStr


class UserCreateSchema(BaseModel):
    email: EmailStr
    password: str


class PaginatedUsersSchema(BaseModel):
    users: List[UserSchema]
    total: int
    page: int
    total_pages: int

