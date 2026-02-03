from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Global configuration object for the application.
    Values can come from environment variables or a .env file.
    """

    app_name: str = "Forest Phenology Tracking System"
    environment: str = "development"
    log_level: str = "info"
    data_dir: str = "data"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
