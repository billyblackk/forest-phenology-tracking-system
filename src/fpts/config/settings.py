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

    # Ingestion for Platery Computer STAC

    pc_stac_url: str = "https://planetarycomputer.microsoft.com/api/stac/v1"
    mod13q1_collection: str = "modis-13Q1-061"
