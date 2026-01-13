"""
Optralis Discord Docs Bot

Main entry point for the Discord documentation bot.
Supports two modes:
- Local file watcher (for local development)
- GitHub webhook (for VPS deployment)
"""

import asyncio
import signal
import sys
import discord
from config import load_config
from utils.logger import setup_logger
from bot.client import DocsBot
from bot.events import setup_events

# Global references for signal handlers
bot_instance = None
watcher_instance = None
webhook_server = None
logger = None


def signal_handler(sig, frame):
    """Handle shutdown signals gracefully."""
    global bot_instance, watcher_instance, webhook_server, logger

    if logger:
        logger.info("\n🛑 Shutdown signal received, cleaning up...")

    # Stop file watcher if running
    if watcher_instance and watcher_instance.is_running:
        watcher_instance.stop()

    # Stop webhook server if running
    if webhook_server:
        asyncio.create_task(webhook_server.stop())

    # Stop bot
    if bot_instance:
        asyncio.create_task(bot_instance.close())

    if logger:
        logger.info("Goodbye!")
    sys.exit(0)


async def main():
    """Main async entry point."""
    global bot_instance, watcher_instance, webhook_server, logger

    try:
        # Load configuration
        print("📋 Loading configuration...")
        config = load_config()
        print("✅ Configuration loaded successfully")

    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\nPlease check your .env file and try again.")
        sys.exit(1)

    except Exception as e:
        print(f"❌ Unexpected error loading configuration: {e}")
        sys.exit(1)

    # Setup logger
    logger = setup_logger(config.log_level, config.log_file)
    logger.info("=" * 60)
    logger.info("🤖 Optralis Discord Docs Bot Starting...")
    logger.info("=" * 60)

    # Log configuration
    logger.info(f"Mode: {'Webhook' if config.use_webhook else 'File Watcher'}")
    logger.info(f"Docs path: {config.docs_path}")
    logger.info(f"Guild ID: {config.guild_id}")

    if config.use_webhook:
        logger.info(f"Webhook port: {config.webhook_port}")
        logger.info(f"Webhook secret: {'configured' if config.webhook_secret else 'NOT SET (insecure!)'}")

    # Create bot instance
    logger.info("🔧 Initializing Discord bot...")
    bot = DocsBot(config)
    bot_instance = bot

    # Setup event handlers and commands
    setup_events(bot)

    # Setup slash commands
    from bot.commands import setup_commands
    setup_commands(bot)

    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Setup mode-specific components
    if config.use_webhook:
        # Webhook mode for VPS deployment
        from webhook.server import WebhookServer
        from webhook.git_handler import GitHandler

        git_handler = GitHandler(bot, config)
        webhook_server = WebhookServer(bot, config, git_handler)

        @bot.event
        async def on_ready():
            """Start webhook server when bot is ready."""
            logger.info(f"Bot connected as {bot.user} (ID: {bot.user.id})")
            logger.info(f"Connected to {len(bot.guilds)} guild(s)")

            # Sync slash commands with Discord
            try:
                guild = discord.Object(id=config.guild_id)
                synced = await bot.tree.sync(guild=guild)
                logger.info(f"Synced {len(synced)} slash command(s)")
            except Exception as e:
                logger.error(f"Failed to sync commands: {e}")

            # Initialize channel resolver
            success = bot.initialize_channel_resolver()

            if success:
                logger.info("✅ Channel resolver initialized")
            else:
                logger.warning("⚠️ Channel setup incomplete. Check logs.")

            # Start webhook server
            try:
                await webhook_server.start()
                logger.info("=" * 60)
                logger.info("✅ Bot fully initialized and ready!")
                logger.info("=" * 60)
                logger.info(f"Webhook endpoint: http://0.0.0.0:{config.webhook_port}/webhook")
                logger.info("Configure this URL in your GitHub repository settings.")
                logger.info("Press Ctrl+C to stop the bot")
            except Exception as e:
                logger.error(f"Failed to start webhook server: {e}")

    else:
        # File watcher mode for local development
        from watcher.file_watcher import DocsWatcher
        from watcher.event_handler import DocsEventHandler

        event_handler = DocsEventHandler(bot, config)
        watcher = DocsWatcher(config, event_handler)
        watcher_instance = watcher

        @bot.event
        async def on_ready():
            """Start file watcher when bot is ready."""
            logger.info(f"Bot connected as {bot.user} (ID: {bot.user.id})")
            logger.info(f"Connected to {len(bot.guilds)} guild(s)")

            # Sync slash commands with Discord
            try:
                guild = discord.Object(id=config.guild_id)
                synced = await bot.tree.sync(guild=guild)
                logger.info(f"Synced {len(synced)} slash command(s)")
            except Exception as e:
                logger.error(f"Failed to sync commands: {e}")

            # Initialize channel resolver
            success = bot.initialize_channel_resolver()

            if success:
                logger.info("✅ Channel resolver initialized")
            else:
                logger.warning("⚠️ Channel setup incomplete. Check logs.")

            # Start file watcher
            if config.auto_start_watcher:
                try:
                    watcher.start()
                    logger.info("=" * 60)
                    logger.info("✅ Bot fully initialized and ready!")
                    logger.info("=" * 60)
                    logger.info(f"Watching: {config.docs_path}")
                    logger.info("Press Ctrl+C to stop the bot")
                except Exception as e:
                    logger.error(f"Failed to start file watcher: {e}")

    try:
        # Start the bot (blocking)
        logger.info("🚀 Starting Discord bot...")
        await bot.start(config.discord_token)

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Bot error: {e}", exc_info=True)
    finally:
        # Cleanup
        logger.info("Cleaning up...")

        if watcher_instance and watcher_instance.is_running:
            watcher_instance.stop()

        if webhook_server:
            await webhook_server.stop()

        if not bot.is_closed():
            await bot.close()

        logger.info("Bot stopped")


if __name__ == "__main__":
    try:
        # Check Python version
        if sys.version_info < (3, 9):
            print("❌ Python 3.9 or higher is required")
            sys.exit(1)

        # Run the async main function
        asyncio.run(main())

    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
