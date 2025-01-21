from typing import Literal
from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MODE: Literal["DEV", "TEST", "PROD"]
    LOG_LEVEL: str

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    TEST_DB_HOST: str
    TEST_DB_PORT: int
    TEST_DB_USER: str
    TEST_DB_PASS: str
    TEST_DB_NAME: str

    SECRET_KEY: str
    ALGORITHM: str

    DATABASE_URL: str = Field(default_factory=str)
    TEST_DATABASE_URL: str = Field(default_factory=str)

    REDIS_HOST: str
    REDIS_PORT: int

    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASS: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.DATABASE_URL = (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"  # noqa F401
        )
        self.TEST_DATABASE_URL = (
            f"postgresql+asyncpg://{self.TEST_DB_USER}:{self.TEST_DB_PASS}@{self.TEST_DB_HOST}:{self.TEST_DB_PORT}/{self.TEST_DB_NAME}"  # noqa F401
        )

    model_config = ConfigDict(env_file=".env")


settings = Settings()

print(settings.DATABASE_URL)
