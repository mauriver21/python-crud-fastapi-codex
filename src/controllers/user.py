from interfaces.UserCreate import UserCreate
from interfaces.UserUpdate import UserUpdate
from interfaces.UserAuth import UserAuth
import repositories.user as user_repository


def login(auth: UserAuth):
    return user_repository.login(auth)


def list(page: int = 0, page_size: int = 10):
    return user_repository.list(page, page_size)


def create(user: UserCreate):
    return user_repository.create(user)


def update(id: str, user: UserUpdate):
    return user_repository.update(id, user)


def remove(id: str):
    return user_repository.logical_delete(id)
