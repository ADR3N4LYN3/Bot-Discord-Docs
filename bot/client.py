"""Discord bot client for Optralis Docs Bot."""

import discord
from discord.ext import commands
from typing import Optional
from utils.logger import get_logger
from utils.channel_resolver import ChannelResolver

logger = get_logger("bot.client")


class DocsBot(commands.Bot):
    """Custom Discord bot for documentation posting."""

    def __init__(self, config):
        """
        Initialize the Discord bot.

        Args:
            config: Configuration object
        """
        self.config = config

        # Setup intents
        intents = discord.Intents.default()
        intents.guilds = True  # Access to guilds and channels
        intents.messages = True  # Access to send messages

        # Initialize bot
        super().__init__(
            command_prefix="!",  # Not used but required
            intents=intents,
            help_command=None,
        )

        self.channel_resolver: Optional[ChannelResolver] = None
        self.target_guild: Optional[discord.Guild] = None

    async def setup_hook(self):
        """Called when the bot is starting up."""
        logger.info("Bot setup hook called")

    def get_target_guild(self) -> Optional[discord.Guild]:
        """
        Get the target guild (server) from config.

        Returns:
            Guild object or None if not found
        """
        if self.target_guild:
            return self.target_guild

        guild = self.get_guild(self.config.guild_id)

        if not guild:
            logger.error(
                f"Could not find guild with ID {self.config.guild_id}. "
                f"Make sure the bot is invited to the server."
            )
            return None

        self.target_guild = guild
        logger.info(f"Found target guild: {guild.name} (ID: {guild.id})")
        return guild

    def initialize_channel_resolver(self):
        """Initialize the channel resolver with guild and channel mapping."""
        guild = self.get_target_guild()

        if not guild:
            logger.error("Cannot initialize channel resolver: guild not found")
            return False

        channel_mapping = self.config.get_channel_mapping()
        self.channel_resolver = ChannelResolver(guild, channel_mapping)

        # Verify all required channels exist
        verification = self.channel_resolver.verify_all_channels_exist()

        missing_channels = [
            name for name, exists in verification.items() if not exists
        ]

        if missing_channels:
            logger.warning(
                f"Missing channels: {', '.join(missing_channels)}. "
                f"Please create them in Discord."
            )
            return False

        logger.info("Channel resolver initialized successfully")
        return True

    async def post_to_channel(
        self, folder_name: str, embeds: list[discord.Embed]
    ) -> bool:
        """
        Post embeds to the appropriate channel based on folder name.

        Args:
            folder_name: Name of the folder (e.g., "specs", "root")
            embeds: List of Discord embeds to post

        Returns:
            True if successful, False otherwise
        """
        if not self.channel_resolver:
            logger.error("Channel resolver not initialized")
            return False

        channel = self.channel_resolver.get_channel(folder_name)

        if not channel:
            logger.error(f"Could not find channel for folder: {folder_name}")
            return False

        try:
            # Post each embed with a delay
            for i, embed in enumerate(embeds):
                await channel.send(embed=embed)
                logger.info(
                    f"Posted message {i + 1}/{len(embeds)} to #{channel.name}"
                )

                # Add delay between messages to avoid rate limiting
                if i < len(embeds) - 1:
                    import asyncio

                    await asyncio.sleep(self.config.message_delay)

            return True

        except discord.Forbidden:
            logger.error(
                f"Missing permissions to post in #{channel.name}. "
                f"Check bot permissions."
            )
            return False

        except discord.HTTPException as e:
            logger.error(f"Failed to post to #{channel.name}: {e}")
            return False

        except Exception as e:
            logger.error(f"Unexpected error posting to #{channel.name}: {e}")
            return False
