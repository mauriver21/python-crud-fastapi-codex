from typing import TypedDict


class DbConfig(TypedDict):
    dialect: str
    host: str
    port: str
    user: str
    password: str
    database: str
