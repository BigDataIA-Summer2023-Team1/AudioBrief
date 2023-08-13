from pydantic import BaseModel


class Users(BaseModel):
    email: str
    password: str
    plan: str


class UsersLogin(BaseModel):
    email: str
    password: str
