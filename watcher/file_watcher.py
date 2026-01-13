"""File system watcher for documentation changes."""

from watchdog.observers import Observer
from pathlib import Path
from utils.logger import get_logger

logger = get_logger("file_watcher")


class DocsWatcher:
    """Watches the documentation folder for changes."""

    def __init__(self, config, event_handler):
        """
        Initialize the documentation watcher.

        Args:
            config: Configuration object
            event_handler: FileSystemEventHandler instance
        """
        self.config = config
        self.event_handler = event_handler
        self.observer = Observer()
        self.is_running = False

    def start(self):
        """Start watching the documentation folder."""
        docs_path = str(self.config.docs_path)

        logger.info(f"Starting file watcher on: {docs_path}")
        logger.info(f"Recursive: {self.config.watch_recursive}")

        try:
            self.observer.schedule(
                self.event_handler,
                docs_path,
                recursive=self.config.watch_recursive,
            )

            self.observer.start()
            self.is_running = True

            logger.info("✅ File watcher started successfully")

        except Exception as e:
            logger.error(f"Failed to start file watcher: {e}")
            raise

    def stop(self):
        """Stop the file watcher."""
        if self.is_running:
            logger.info("Stopping file watcher...")
            self.observer.stop()
            self.observer.join()
            self.is_running = False
            logger.info("File watcher stopped")

    def is_markdown_file(self, file_path: str) -> bool:
        """
        Check if a file is a markdown file.

        Args:
            file_path: Path to the file

        Returns:
            True if markdown file, False otherwise
        """
        path = Path(file_path)
        return path.suffix.lower() in (".md", ".markdown")
