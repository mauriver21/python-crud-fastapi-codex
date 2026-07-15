from sqlmodel import SQLModel

from db.schema.users import User
from interfaces.UserPagination import UserPagination


class UserModelList(SQLModel):
    data: list[User]
    pagination: UserPagination
