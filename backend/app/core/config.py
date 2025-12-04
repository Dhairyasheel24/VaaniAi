from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables or .env file.
    """
    PROJECT_NAME: str = "VaaniAi Backend"
    VERSION: str = "1.0.0"
    
    # AI Configuration
    GEMINI_API_KEY: str

    # Pydantic Settings Config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore"
    )

settings = Settings()