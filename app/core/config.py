from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # Application configuration
    app_name: str = "ShopEase User Management Service"
    app_env: str = "development"

    # MySQL database configuration
    db_host: str
    db_port: int = 3306
    db_name: str
    db_user: str
    db_password: SecretStr

    # Authentication Service configuration
    auth_service_verify_url: str
    auth_service_timeout_seconds: float = 5.0

    # Read configuration from environment variables and .env
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Create one reusable configuration object
settings = Settings()
