from datetime import timedelta

import jwt

from config import config
from db.schema.users import User
from interfaces import UserAuthResponse
from interfaces.UserAuth import UserAuth
from interfaces.UserCreate import UserCreate
from interfaces.UserUpdate import UserUpdate
from pwdlib import PasswordHash
import models.user as user_model
from utils.utc_now import utc_now

password_hash = PasswordHash.recommended()


def sanitize_user(user: User):
    return user.model_dump(exclude={"password"})


def list(page: int = 0, page_size: int = 10):
    try:
        result = user_model.list(page, page_size)
        result.data = [{**sanitize_user(user)} for user in result.data]
        return result
    except Exception as error:
        raise Exception(f"[User repo] Failed user listing: {str(error)}") from error


def create(user: UserCreate):
    try:
        user.password = password_hash.hash(user.password)
        result = sanitize_user(user_model.create(user))
        return result
    except Exception as error:
        raise Exception(f"[User repo] Failed user creation: {str(error)}") from error


def update(id: str, user: UserUpdate):
    try:
        return sanitize_user(user_model.update(id, user))
    except Exception as error:
        raise Exception(f"[User repo] Failed user updating: {str(error)}") from error


def logical_delete(id: str):
    try:
        return sanitize_user(user_model.logical_delete(id))
    except Exception as error:
        raise Exception(f"[User repo] Failed user removing: {str(error)}") from error


def login(auth: UserAuth) -> UserAuthResponse:
    try:
        found_user = user_model.find_by_email(auth["email"])
        if found_user is None:
            raise Exception("The user is not registered")

        verified = password_hash.verify(auth["password"], found_user.password)
        if verified is False:
            raise Exception("Invalid password")

        user = sanitize_user(found_user)
        to_encode = user.copy()
        to_encode.update(
            {
                "exp": (
                    utc_now() + timedelta(hours=config["jwtExpiresInHours"])
                ).timestamp()
            }
        )

        token = jwt.encode(
            to_encode,
            config["jwtSecretKey"],
            algorithm="HS256",
        )

        return {"token": token, "user": user}
    except Exception as error:
        raise Exception(f"[User repo] User login failed: {str(error)}") from error
