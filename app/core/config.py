from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(
    BaseSettings
):

    SUPABASE_URL: str

    SUPABASE_ANON_KEY: str

    SUPABASE_SERVICE_ROLE_KEY: str

    DATABASE_URL: str

    GOOGLE_CLIENT_ID: str

    GOOGLE_CLIENT_SECRET: str

    JWT_SECRET: str

    JWT_ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    ENV: str = "development"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()