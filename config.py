"""Configuration loader and validator for Discord Docs Bot."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class Config:
    """Bot configuration loaded from environment variables."""

    def __init__(self):
        """Load and validate configuration from .env file."""
        load_dotenv()

        # Discord Configuration
        self.discord_token = self._get_required("DISCORD_BOT_TOKEN")
        self.guild_id = self._get_required_int("GUILD_ID")

        # Documentation Path
        self.docs_path = Path(self._get_required("DOCS_PATH"))

        # Bot Behavior
        self.auto_start_watcher = self._get_bool("AUTO_START_WATCHER", True)
        self.watch_recursive = self._get_bool("WATCH_RECURSIVE", True)

        # Message Formatting
        self.embed_color = int(self._get_env("EMBED_COLOR", "0x5865F2"), 16)
        self.max_message_length = self._get_int("MAX_MESSAGE_LENGTH", 2000)
        self.message_delay = self._get_float("MESSAGE_DELAY", 0.5)

        # Logging
        self.log_level = self._get_env("LOG_LEVEL", "INFO")
        self.log_file = self._get_env("LOG_FILE", "bot.log")

        # Webhook Configuration (for VPS deployment)
        self.use_webhook = self._get_bool("USE_WEBHOOK", False)
        self.webhook_port = self._get_int("WEBHOOK_PORT", 8080)
        self.webhook_secret = os.getenv("WEBHOOK_SECRET", "")

        # Validate configuration
        self._validate()

    def _get_env(self, key: str, default: Optional[str] = None) -> str:
        """Get environment variable with optional default."""
        value = os.getenv(key)
        if value is None:
            if default is not None:
                return default
            raise ValueError(f"Missing required environment variable: {key}")
        return value

    def _get_required(self, key: str) -> str:
        """Get required environment variable."""
        return self._get_env(key)

    def _get_int(self, key: str, default: int) -> int:
        """Get integer environment variable."""
        value = os.getenv(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            raise ValueError(f"Invalid integer value for {key}: {value}")

    def _get_required_int(self, key: str) -> int:
        """Get required integer environment variable."""
        value = self._get_required(key)
        try:
            return int(value)
        except ValueError:
            raise ValueError(f"Invalid integer value for {key}: {value}")

    def _get_float(self, key: str, default: float) -> float:
        """Get float environment variable."""
        value = os.getenv(key)
        if value is None:
            return default
        try:
            return float(value)
        except ValueError:
            raise ValueError(f"Invalid float value for {key}: {value}")

    def _get_bool(self, key: str, default: bool) -> bool:
        """Get boolean environment variable."""
        value = os.getenv(key)
        if value is None:
            return default
        return value.lower() in ("true", "1", "yes", "on")

    def _validate(self):
        """Validate configuration values."""
        # Validate docs path exists (only if not using webhook or if path is set)
        if not self.use_webhook:
            if not self.docs_path.exists():
                raise ValueError(
                    f"Documentation path does not exist: {self.docs_path}\n"
                    f"Please create the directory or update DOCS_PATH in .env"
                )

            if not self.docs_path.is_dir():
                raise ValueError(
                    f"Documentation path is not a directory: {self.docs_path}"
                )

        # Validate max message length
        if self.max_message_length > 2000:
            raise ValueError(
                f"MAX_MESSAGE_LENGTH cannot exceed 2000 (Discord limit), got: {self.max_message_length}"
            )

        if self.max_message_length < 100:
            raise ValueError(
                f"MAX_MESSAGE_LENGTH too small: {self.max_message_length}"
            )

    def get_channel_mapping(self) -> dict[str, str]:
        """
        Get folder to channel name mapping.

        Returns:
            Dict mapping folder names to Discord channel names
        """
        return {
            "root": "documentation",
            "specs": "specifications",
            "implementation": "implementation",
            "plans": "planning",
        }


def load_config() -> Config:
    """
    Load and return bot configuration.

    Returns:
        Config object with validated settings

    Raises:
        ValueError: If required config is missing or invalid
    """
    return Config()
