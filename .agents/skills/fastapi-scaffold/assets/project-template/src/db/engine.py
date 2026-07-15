from sqlmodel import create_engine

from config import config

db = config["db"]

CONNECTION_URL = f"{db["dialect"]}+psycopg://{db["user"]}:{db["password"]}@{db["host"]}:{db["port"]}/{db["database"]}"

engine = create_engine(
    CONNECTION_URL,
    echo=True,
    pool_pre_ping=True,
)
