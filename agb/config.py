import json
import os
from typing import Any, Dict, Optional
import dotenv
from pathlib import Path

# Browser configuration constants
BROWSER_DATA_PATH = "/tmp/agb_browser_data"


class Config:
    """Configuration class for AGB client."""

    def __init__(self, endpoint: str, timeout_ms: int):
        self.endpoint = endpoint
        self.timeout_ms = timeout_ms


def default_config() -> Config:
    """Return the default configuration"""
    return Config(
        endpoint="sdk-api.agb.cloud",
        timeout_ms=60000,
    )


"""
The SDK uses the following precedence order for configuration (highest to lowest):
1. Explicitly passed configuration in code.
2. Environment variables.
3. .env file.
4. Default configuration.
"""


def load_config(cfg: Optional[Config] = None) -> Config:
    """Load configuration with the specified precedence order."""
    if cfg is not None:
        # Return directly
        return cfg
    else:
        config = default_config()
        try:
            env_path = Path(os.getcwd()) / ".env"
            dotenv.load_dotenv(env_path)
        except:
            print("Warning: Failed to load .env file")

        if endpoint := os.getenv("AGB_ENDPOINT"):
            config.endpoint = endpoint
        if timeout_ms := os.getenv("AGB_TIMEOUT_MS"):
            config.timeout_ms = int(timeout_ms)

    return config
