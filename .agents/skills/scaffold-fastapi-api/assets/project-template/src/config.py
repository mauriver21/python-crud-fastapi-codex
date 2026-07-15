import os
from pathlib import Path

from dotenv import load_dotenv

from interfaces.Config import Config

ENVIRONMENT = os.getenv("APP_ENV", "development")
ENV_FILE_NAMES = {
    "test": ".env.test",
    "development": ".env.dev",
    "production": ".env.prod",
}
ENV_FILE_NAME = ENV_FILE_NAMES.get(ENVIRONMENT, ".env.dev")
ENV_PATH = Path(__file__).resolve().parents[1] / ENV_FILE_NAME

load_dotenv(ENV_PATH)


config: Config = {
    "environment": ENVIRONMENT,
    "allowedOrigins": os.getenv("ALLOWED_ORIGINS").split(","),
    "port": int(os.getenv("PORT", "3000")),
    "jwtExpiresInHours": int(os.getenv("JWT_EXPIRES_IN_HOURS", "3000")),
    "jwtSecretKey": os.getenv("JWT_SECRET_KEY"),
    "diskStoragePath": os.getenv("DISK_STORAGE_PATH"),
    "db": {
        "dialect": os.getenv("DB_DIALECT", "postgresql"),
        "host": os.getenv("DB_HOST", "127.0.0.1"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", "1234"),
        "database": os.getenv("DB_NAME", "my-database"),
    },
}
