"""File system event handler for documentation changes."""

import asyncio
from pathlib import Path
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent
from utils.logger import get_logger
from processors.markdown_parser import MarkdownParser
from processors.message_splitter import MessageSplitter
from processors.embed_builder import EmbedBuilder

logger = get_logger("event_handler")


class DocsEventHandler(FileSystemEventHandler):
    """Handles file system events for documentation files."""

    def __init__(self, bot, config):
        """
        Initialize the event handler.

        Args:
            bot: DocsBot instance
            config: Configuration object
        """
        super().__init__()
        self.bot = bot
        self.config = config

        # Initialize processors
        self.parser = MarkdownParser()
        self.splitter = MessageSplitter(max_length=config.max_message_length - 100)
        self.embed_builder = EmbedBuilder(embed_color=config.embed_color)

        # Debouncing: track last processed time for each file
        self.last_processed = {}
        self.debounce_seconds = 2

    def on_modified(self, event):
        """Called when a file is modified."""
        if event.is_directory:
            return

        if self._is_markdown_file(event.src_path):
            logger.info(f"File modified: {event.src_path}")
            self._process_file(event.src_path, "modified")

    def on_created(self, event):
        """Called when a file is created."""
        if event.is_directory:
            return

        if self._is_markdown_file(event.src_path):
            logger.info(f"File created: {event.src_path}")
            self._process_file(event.src_path, "created")

    def on_deleted(self, event):
        """Called when a file is deleted."""
        if event.is_directory:
            return

        if self._is_markdown_file(event.src_path):
            logger.info(f"File deleted: {event.src_path}")
            # Optionally handle deletions (e.g., post a deletion notice)

    def _is_markdown_file(self, file_path: str) -> bool:
        """Check if file is a markdown file."""
        path = Path(file_path)
        return path.suffix.lower() in (".md", ".markdown")

    def _should_process(self, file_path: str) -> bool:
        """
        Check if file should be processed (debouncing).

        Args:
            file_path: Path to the file

        Returns:
            True if should process, False if too soon
        """
        import time

        now = time.time()
        last_time = self.last_processed.get(file_path, 0)

        if now - last_time < self.debounce_seconds:
            logger.debug(f"Debouncing file: {file_path}")
            return False

        self.last_processed[file_path] = now
        return True

    def _process_file(self, file_path: str, event_type: str):
        """
        Process a file change and post to Discord.

        Args:
            file_path: Path to the changed file
            event_type: Type of event (created, modified, deleted)
        """
        # Debounce
        if not self._should_process(file_path):
            return

        # Run async processing in the event loop
        asyncio.run_coroutine_threadsafe(
            self._process_file_async(file_path, event_type),
            self.bot.loop
        )

    async def _process_file_async(self, file_path: str, event_type: str):
        """
        Async processing of file changes.

        Args:
            file_path: Path to the file
            event_type: Type of event
        """
        try:
            # Read file content
            content = await self._read_file(file_path)

            if not content:
                logger.warning(f"File is empty: {file_path}")
                return

            # Extract folder for channel mapping
            folder_name = self._extract_folder(file_path)
            file_name = Path(file_path).name

            logger.info(
                f"Processing {file_name} (event: {event_type}, folder: {folder_name})"
            )

            # Parse markdown
            parsed_doc = self.parser.parse_file(file_path, content)

            # Split content into chunks
            chunks = self.splitter.split_with_metadata(
                parsed_doc.content, file_name
            )

            logger.info(
                f"Split {file_name} into {len(chunks)} chunk(s)"
            )

            # Create embeds
            embeds = self.embed_builder.create_embeds_from_chunks(
                parsed_doc, chunks
            )

            # Post to Discord
            success = await self.bot.post_to_channel(folder_name, embeds)

            if success:
                logger.info(
                    f"✅ Successfully posted {file_name} to Discord "
                    f"({len(embeds)} message(s))"
                )
            else:
                logger.error(f"❌ Failed to post {file_name} to Discord")

        except Exception as e:
            logger.error(
                f"Error processing file {file_path}: {e}",
                exc_info=True
            )

    async def _read_file(self, file_path: str) -> str:
        """
        Read file content asynchronously.

        Args:
            file_path: Path to the file

        Returns:
            File content as string
        """
        try:
            import aiofiles

            async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                content = await f.read()
                return content

        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return ""

    def _extract_folder(self, file_path: str) -> str:
        """
        Extract the folder name for channel mapping.

        Args:
            file_path: Path to the file

        Returns:
            Folder name (e.g., "specs", "root", "plans")
        """
        file_path = Path(file_path)
        docs_base = self.config.docs_path

        try:
            relative = file_path.relative_to(docs_base)

            # If file is at root of docs/
            if len(relative.parts) == 1:
                return "root"

            # Return first folder in path
            return relative.parts[0]

        except ValueError:
            # File is not under docs_base
            logger.warning(
                f"File {file_path} is not under docs base {docs_base}"
            )
            return "root"
