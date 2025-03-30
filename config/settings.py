"""Module for managing configuration settings."""

from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field

# Load environment variables from .env file
load_dotenv(override=True)

class Settings(BaseSettings):
    """Class for managing configuration settings."""

    anthropic_api_key: str = Field(..., env='ANTHROPIC_API_KEY')
    anthropic_model: str = Field(
        default="claude-3-7-sonnet-20250219",
        env='ANTHROPIC_MODEL'
    )
    planning_model: str = Field(
        default="claude-3-haiku-20240307",
        env='PLANNING_MODEL'
    )
    max_tokens_response: int = Field(
        default=4096,
        env='MAX_TOKENS_RESPONSE'
    )
    planning_temperature: float = Field(
        default=0.2,
        env='PLANNING_TEMPERATURE'
    )
    execution_temperature: float = Field(
        default=0.7,
        env='EXECUTION_TEMPERATURE'
    )

    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
