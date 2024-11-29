from pydantic import model_validator, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    DATABASE_URL: str = Field(default_factory=str)

    @model_validator(mode="after")
    def get_database_url(cls, model):
        model.DATABASE_URL = (
            f"postgresql+asyncpg://{model.DB_USER}:{model.DB_PASS}@{model.DB_HOST}:{model.DB_PORT}/{model.DB_NAME}"  # noqa F401
        )
        return model

    class Config:
        env_file = ".env"


settings = Settings()

print(settings.DATABASE_URL)
