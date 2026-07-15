from typing import TypedDict

from interfaces.DbConfig import DbConfig


class Config(TypedDict):
    environment: str
    allowedOrigins: str
    port: int
    jwtExpiresIn: str
    jwtSecretKey: str
    diskStoragePath: str
    db: DbConfig
