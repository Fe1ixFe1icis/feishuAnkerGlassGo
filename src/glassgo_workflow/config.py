"""Configuration loading utilities."""

import os
from pathlib import Path

from dotenv import load_dotenv


def load_env() -> None:
    """Load environment variables from .env if present."""
    env_path = Path(".env")
    if env_path.exists():
        load_dotenv(env_path)


def get_default_llm_provider() -> str:
    return os.getenv("DEFAULT_LLM_PROVIDER", "openai").lower()


def get_default_model(provider: str | None = None) -> str:
    provider = provider or get_default_llm_provider()
    if provider == "openai":
        return os.getenv("OPENAI_MODEL", "gpt-4o")
    if provider == "anthropic":
        return os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    raise ValueError(f"Unsupported provider: {provider}")


def get_temperature() -> float:
    return float(os.getenv("LLM_TEMPERATURE", "0.4"))


def get_api_key(provider: str) -> str:
    key = os.getenv(f"{provider.upper()}_API_KEY")
    if not key:
        raise ValueError(
            f"Missing {provider.upper()}_API_KEY. "
            "Set it in .env or as an environment variable."
        )
    return key
