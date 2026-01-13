"""
Optralis Discord Docs Bot

Main entry point for the Discord documentation bot.
"""

import asyncio
import signal
import sys
from config import load_config
from utils.logger import setup_logger
from bot.client import DocsBot
from bot.events import setup_events
from watcher.file_watcher import DocsWatcher
from watcher.event_handler import DocsEventHandler

# Global references for signal handlers
bot_instance = None
watcher_instance = None
logger = None


def signal_handler(sig, frame):
    """Handle shutdown signals gracefully."""
    global bot_instance, watcher_instance, logger

    logger.info("\n🛑 Shutdown signal received, cleaning up...")

    # Stop file watcher
    if watcher_instance and watcher_instance.is_running:
        watcher_instance.stop()

    # Stop bot
    if bot_instance:
        asyncio.create_task(bot_instance.close())

    logger.info("Goodbye!")
    sys.exit(0)


async def main():
    """Main async entry point."""
    global bot_instance, watcher_instance, logger

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
    logger.info(f"Docs path: {config.docs_path}")
    logger.info(f"Guild ID: {config.guild_id}")
    logger.info(f"Max message length: {config.max_message_length}")
    logger.info(f"Auto-start watcher: {config.auto_start_watcher}")

    # Create bot instance
    logger.info("🔧 Initializing Discord bot...")
    bot = DocsBot(config)
    bot_instance = bot

    # Setup event handlers
    setup_events(bot)

    # Create file watcher event handler
    event_handler = DocsEventHandler(bot, config)

    # Create file watcher
    watcher = DocsWatcher(config, event_handler)
    watcher_instance = watcher

    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Add on_ready hook to start file watcher
    original_on_ready = bot.get_cog("DocsBot") or bot

    @bot.event
    async def on_ready():
        """Extended on_ready to start file watcher."""
        # Call original on_ready logic
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

        # Start file watcher
        if config.auto_start_watcher:
            try:
                watcher.start()
                logger.info("=" * 60)
                logger.info("✅ Bot fully initialized and ready!")
                logger.info("=" * 60)
                logger.info(
                    f"Watching: {config.docs_path}"
                )
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

        if watcher.is_running:
            watcher.stop()

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
