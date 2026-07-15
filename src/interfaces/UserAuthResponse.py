from typing import TypedDict

from db.schema.users import User


class UserAuthResponse(TypedDict):
    token: str
    user: User
