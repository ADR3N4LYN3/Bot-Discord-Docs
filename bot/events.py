"""Discord event handlers for the bot."""

import discord
from utils.logger import get_logger

logger = get_logger("bot.events")


def setup_events(bot):
    """
    Setup event handlers for the bot.

    Args:
        bot: DocsBot instance
    """

    @bot.event
    async def on_ready():
        """Called when the bot successfully connects to Discord."""
        logger.info(f"Bot connected as {bot.user} (ID: {bot.user.id})")
        logger.info(f"Connected to {len(bot.guilds)} guild(s)")

        # Initialize channel resolver
        success = bot.initialize_channel_resolver()

        if success:
            logger.info("✅ Bot is ready to receive file events")
        else:
            logger.warning(
                "⚠️ Bot connected but channel setup incomplete. "
                "Check logs for missing channels."
            )

    @bot.event
    async def on_guild_available(guild: discord.Guild):
        """Called when a guild becomes available."""
        logger.info(f"Guild available: {guild.name} (ID: {guild.id})")

        # Refresh channel cache if this is our target guild
        if bot.target_guild and guild.id == bot.target_guild.id:
            if bot.channel_resolver:
                bot.channel_resolver.refresh_cache()

    @bot.event
    async def on_guild_channel_create(channel: discord.abc.GuildChannel):
        """Called when a channel is created."""
        if isinstance(channel, discord.TextChannel):
            logger.info(f"New text channel created: #{channel.name}")

            # Refresh cache if this is our target guild
            if bot.channel_resolver and channel.guild.id == bot.config.guild_id:
                bot.channel_resolver.refresh_cache()

    @bot.event
    async def on_guild_channel_delete(channel: discord.abc.GuildChannel):
        """Called when a channel is deleted."""
        if isinstance(channel, discord.TextChannel):
            logger.warning(f"Text channel deleted: #{channel.name}")

            # Refresh cache if this is our target guild
            if bot.channel_resolver and channel.guild.id == bot.config.guild_id:
                bot.channel_resolver.refresh_cache()

    @bot.event
    async def on_guild_channel_update(
        before: discord.abc.GuildChannel, after: discord.abc.GuildChannel
    ):
        """Called when a channel is updated."""
        if isinstance(after, discord.TextChannel):
            if before.name != after.name:
                logger.info(
                    f"Channel renamed: #{before.name} → #{after.name}"
                )

                # Refresh cache if this is our target guild
                if bot.channel_resolver and after.guild.id == bot.config.guild_id:
                    bot.channel_resolver.refresh_cache()

    @bot.event
    async def on_error(event: str, *args, **kwargs):
        """Called when an event handler raises an exception."""
        logger.error(f"Error in event {event}", exc_info=True)

    @bot.event
    async def on_disconnect():
        """Called when the bot disconnects from Discord."""
        logger.warning("Bot disconnected from Discord")

    @bot.event
    async def on_resumed():
        """Called when the bot resumes a session."""
        logger.info("Bot session resumed")

    logger.info("Event handlers registered")
