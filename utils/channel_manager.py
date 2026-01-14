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
        channel_mapping: dict = None,
        auto_create: bool = True,
    ):
        """
        Initialize the channel manager.

        Args:
            guild: Discord guild (server)
            category_id: ID of the category for doc channels
            channel_mapping: Dict mapping folder paths to channel names
            auto_create: Whether to auto-create missing channels
        """
        self.guild = guild
        self.category_id = category_id
        self.channel_mapping = channel_mapping or {}
        self.auto_create = auto_create
        self._category_cache: Optional[discord.CategoryChannel] = None
        self._channel_cache: dict = {}
        self._build_channel_cache()

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

    def _build_channel_cache(self):
        """Build a cache of channel names to channel objects."""
        category = self.guild.get_channel(self.category_id)
        if not category:
            logger.warning(f"Category {self.category_id} not found")
            return

        for channel in category.text_channels:
            # Normalize: lowercase, no dashes/underscores
            normalized = channel.name.lower().replace("-", "").replace("_", "")
            self._channel_cache[normalized] = channel
            logger.debug(f"Cached channel: {channel.name} → {normalized}")

        logger.info(f"Built channel cache: {len(self._channel_cache)} channels")

    def get_channel_for_path(self, relative_path: str) -> Optional[discord.TextChannel]:
        """
        Get the channel for a file based on its relative path and the mapping.

        Args:
            relative_path: Path relative to docs root (e.g., "02-developers/backend/API.md")

        Returns:
            TextChannel if found, None otherwise
        """
        from pathlib import Path
        path = Path(relative_path)

        # First, try exact file path match (for file-specific mappings)
        normalized_path = str(path).replace("\\", "/")
        if normalized_path in self.channel_mapping:
            channel_name = self.channel_mapping[normalized_path]
            return self._find_channel_by_name(channel_name)

        # Try to find a matching folder mapping (most specific first)
        parts = path.parts[:-1]  # Remove filename, keep folders

        # Try progressively shorter paths
        for i in range(len(parts), 0, -1):
            folder_path = "/".join(parts[:i])
            if folder_path in self.channel_mapping:
                channel_name = self.channel_mapping[folder_path]
                return self._find_channel_by_name(channel_name)

        # Fallback to "root" if file is at docs root
        if len(parts) == 0 and "root" in self.channel_mapping:
            channel_name = self.channel_mapping["root"]
            return self._find_channel_by_name(channel_name)

        logger.warning(f"No mapping found for path: {relative_path}")
        return None

    def _find_channel_by_name(self, channel_name: str) -> Optional[discord.TextChannel]:
        """Find a channel by name using the cache."""
        normalized = channel_name.lower().replace("-", "").replace("_", "")
        channel = self._channel_cache.get(normalized)

        if channel:
            logger.debug(f"Found channel '{channel_name}' → #{channel.name}")
        else:
            logger.warning(f"Channel '{channel_name}' not found in cache")

        return channel

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
