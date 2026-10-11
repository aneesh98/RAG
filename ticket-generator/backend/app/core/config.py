from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://helpdesk:helpdesk@localhost:5432/helpdesk"
    cors_origins: str = "http://localhost:5173"
    demo_auth_enabled: bool = True
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
