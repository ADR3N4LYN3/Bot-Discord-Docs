"""Manage Discord channel creation and resolution."""

import re
from typing import Optional
import discord
from utils.logger import get_logger

logger = get_logger("channel_manager")


class ChannelManager:
    """Manages Discord channel creation and resolution for documentation files."""

    def __init__(
        self,
        guild: discord.Guild,
        category_id: int = 0,
        auto_create: bool = True,
    ):
        """
        Initialize the channel manager.

        Args:
            guild: Discord guild (server)
            category_id: ID of the category for doc channels
            auto_create: Whether to auto-create missing channels
        """
        self.guild = guild
        self.category_id = category_id
        self.auto_create = auto_create
        self._category_cache: Optional[discord.CategoryChannel] = None

    def filename_to_channel(self, filename: str) -> str:
        """
        Convert a filename to a valid Discord channel name.

        Rules:
        - Remove .md extension
        - Convert to lowercase
        - Replace underscores and spaces with hyphens
        - Remove invalid characters
        - Max 100 characters

        Args:
            filename: File name (e.g., "BACKEND_SPECS.md")

        Returns:
            Channel name (e.g., "backend-specs")
        """
        # Remove extension
        name = filename.replace(".md", "").replace(".MD", "")

        # Convert to lowercase
        name = name.lower()

        # Replace underscores and spaces with hyphens
        name = name.replace("_", "-").replace(" ", "-")

        # Remove invalid characters (Discord allows: a-z, 0-9, -)
        name = re.sub(r"[^a-z0-9-]", "", name)

        # Remove consecutive hyphens
        name = re.sub(r"-+", "-", name)

        # Remove leading/trailing hyphens
        name = name.strip("-")

        # Limit length (Discord max is 100 chars)
        if len(name) > 100:
            name = name[:100].rstrip("-")

        logger.debug(f"Converted filename '{filename}' → channel '{name}'")

        return name

    async def ensure_category_exists(self) -> Optional[discord.CategoryChannel]:
        """
        Get the documentation category by ID.

        Returns:
            CategoryChannel object or None if not found

        Raises:
            ValueError: If category ID is not configured
        """
        # Check cache first
        if self._category_cache and self._category_cache in self.guild.categories:
            return self._category_cache

        # Category ID must be set
        if not self.category_id:
            raise ValueError("DOCS_CATEGORY_ID is not configured in .env")

        # Get category by ID
        category = self.guild.get_channel(self.category_id)

        if category and isinstance(category, discord.CategoryChannel):
            self._category_cache = category
            logger.debug(f"Found category: {category.name} (ID: {category.id})")
            return category

        logger.error(f"Category with ID {self.category_id} not found")
        return None

    async def find_channel(self, channel_name: str) -> Optional[discord.TextChannel]:
        """
        Find an existing text channel by name.

        Args:
            channel_name: Channel name to find

        Returns:
            TextChannel object if found, None otherwise
        """
        # Normalize channel name
        normalized_name = channel_name.lower().replace("-", "").replace("_", "")

        for channel in self.guild.text_channels:
            # Normalize existing channel name
            existing_normalized = (
                channel.name.lower().replace("-", "").replace("_", "")
            )

            if existing_normalized == normalized_name:
                logger.debug(f"Found existing channel: {channel.name}")
                return channel

        return None

    async def ensure_channel_exists(
        self, filename: str
    ) -> Optional[discord.TextChannel]:
        """
        Ensure a channel exists for the given filename.

        This method:
        1. Converts filename to channel name
        2. Searches for existing channel
        3. Creates channel in DOCS category if not found (if auto-create enabled)
        4. Returns the TextChannel object

        Args:
            filename: File name (e.g., "BACKEND_SPECS.md")

        Returns:
            TextChannel object, or None if channel not found and auto-create disabled

        Raises:
            discord.Forbidden: If bot lacks permissions
        """
        # Convert filename to channel name
        channel_name = self.filename_to_channel(filename)

        # Try to find existing channel
        channel = await self.find_channel(channel_name)
        if channel:
            return channel

        # Channel not found
        if not self.auto_create:
            logger.warning(
                f"Channel '{channel_name}' not found and auto-create is disabled"
            )
            return None

        # Create channel in DOCS category
        logger.info(f"Creating channel: #{channel_name}")
        category = await self.ensure_category_exists()

        try:
            channel = await self.guild.create_text_channel(
                name=channel_name, category=category
            )
            logger.info(f"Created channel: #{channel.name} (ID: {channel.id})")
            return channel
        except discord.Forbidden:
            logger.error(
                "Failed to create channel: Bot lacks 'Manage Channels' permission"
            )
            raise
        except Exception as e:
            logger.error(f"Failed to create channel '{channel_name}': {e}")
            raise

    async def get_or_create_channel(
        self, filename: str
    ) -> Optional[discord.TextChannel]:
        """
        Alias for ensure_channel_exists for backwards compatibility.

        Args:
            filename: File name

        Returns:
            TextChannel object or None
        """
        return await self.ensure_channel_exists(filename)
