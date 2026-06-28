from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://blitzx:blitzx@localhost:5432/blitzx"

    JWT_SECRET: str = "dev-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    COOKIE_DOMAIN: str = "localhost"
    COOKIE_SECURE: bool = False

    FRONTEND_ORIGIN: str = "http://localhost:3000"

    ENVIRONMENT: str = "development"


settings = Settings()
