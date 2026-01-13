"""Channel name to ID resolution for Discord."""

import discord
from typing import Optional, Dict
from utils.logger import get_logger

logger = get_logger("channel_resolver")


class ChannelResolver:
    """Resolves folder names to Discord channel IDs."""

    def __init__(self, guild: discord.Guild, channel_mapping: Dict[str, str]):
        """
        Initialize the channel resolver.

        Args:
            guild: Discord guild (server)
            channel_mapping: Dict mapping folder names to channel names
        """
        self.guild = guild
        self.channel_mapping = channel_mapping
        self.cache: Dict[str, int] = {}
        self._build_cache()

    def _build_cache(self):
        """Build cache of channel names to IDs."""
        logger.debug(f"Building channel cache for guild: {self.guild.name}")

        for channel in self.guild.text_channels:
            # Store normalized name
            normalized_name = channel.name.lower().replace("-", "").replace("_", "")
            self.cache[normalized_name] = channel.id
            logger.debug(f"Cached channel: {channel.name} (ID: {channel.id})")

        logger.info(f"Channel cache built: {len(self.cache)} channels found")

    def resolve_channel(self, folder_name: str) -> Optional[int]:
        """
        Resolve a folder name to a Discord channel ID.

        Args:
            folder_name: Name of the folder (e.g., "specs", "root")

        Returns:
            Channel ID if found, None otherwise
        """
        # Get the target channel name from mapping
        target_channel_name = self.channel_mapping.get(folder_name, folder_name)

        # Normalize the channel name
        normalized = target_channel_name.lower().replace("-", "").replace("_", "")

        # Look up in cache
        channel_id = self.cache.get(normalized)

        if channel_id:
            logger.debug(
                f"Resolved folder '{folder_name}' → channel '{target_channel_name}' (ID: {channel_id})"
            )
            return channel_id
        else:
            logger.warning(
                f"Could not resolve folder '{folder_name}' to channel '{target_channel_name}'. "
                f"Available channels: {list(self.cache.keys())}"
            )
            return None

    def refresh_cache(self):
        """Refresh the channel cache (call if channels are added/removed)."""
        logger.info("Refreshing channel cache")
        self.cache.clear()
        self._build_cache()

    def get_channel(self, folder_name: str) -> Optional[discord.TextChannel]:
        """
        Get a Discord TextChannel object for a folder name.

        Args:
            folder_name: Name of the folder

        Returns:
            TextChannel object if found, None otherwise
        """
        channel_id = self.resolve_channel(folder_name)
        if channel_id:
            return self.guild.get_channel(channel_id)
        return None

    def verify_all_channels_exist(self) -> Dict[str, bool]:
        """
        Verify that all required channels exist in the guild.

        Returns:
            Dict mapping channel names to existence status
        """
        results = {}

        for folder_name, channel_name in self.channel_mapping.items():
            normalized = channel_name.lower().replace("-", "").replace("_", "")
            exists = normalized in self.cache
            results[channel_name] = exists

            if exists:
                logger.info(f"✅ Channel '{channel_name}' exists")
            else:
                logger.error(
                    f"❌ Channel '{channel_name}' NOT FOUND - Please create it in Discord"
                )

        return results
