"""Git operations handler for pulling changes and detecting diffs."""

import asyncio
import subprocess
from pathlib import Path
from typing import List
from utils.logger import get_logger
from processors.markdown_parser import MarkdownParser
from processors.message_splitter import MessageSplitter
from processors.embed_builder import EmbedBuilder

logger = get_logger("webhook.git_handler")


class GitHandler:
    """Handles git operations for the webhook server."""

    def __init__(self, bot, config):
        """
        Initialize the git handler.

        Args:
            bot: DocsBot instance
            config: Configuration object
        """
        self.bot = bot
        self.config = config
        self.repo_path = config.docs_path.parent  # Repo root (parent of docs/)

        # Initialize processors
        self.parser = MarkdownParser()
        self.splitter = MessageSplitter(max_length=config.max_message_length - 100)
        self.embed_builder = EmbedBuilder(embed_color=config.embed_color)

    async def pull_and_process(self, modified_files: List[str]):
        """
        Pull latest changes and process modified files.

        Args:
            modified_files: List of modified file paths (relative to repo root)
        """
        try:
            # Run git pull
            success = await self._git_pull()

            if not success:
                logger.error("Git pull failed, skipping file processing")
                return

            # Process each modified file
            for file_path in modified_files:
                await self._process_file(file_path)

        except Exception as e:
            logger.error(f"Error in pull_and_process: {e}", exc_info=True)

    async def _git_pull(self) -> bool:
        """
        Execute git pull.

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Running git pull in {self.repo_path}")

            # Run git pull asynchronously
            process = await asyncio.create_subprocess_exec(
                "git", "pull", "--ff-only",
                cwd=str(self.repo_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                output = stdout.decode().strip()
                logger.info(f"Git pull successful: {output}")
                return True
            else:
                error = stderr.decode().strip()
                logger.error(f"Git pull failed: {error}")
                return False

        except Exception as e:
            logger.error(f"Error running git pull: {e}")
            return False

    async def _process_file(self, relative_path: str):
        """
        Process a single modified file and post to Discord.

        Args:
            relative_path: Path relative to repo root (e.g., "docs/specs/AGENT_SPECS.md")
        """
        try:
            full_path = self.repo_path / relative_path

            if not full_path.exists():
                logger.warning(f"File not found after pull: {full_path}")
                return

            # Read file content
            content = full_path.read_text(encoding="utf-8")

            if not content:
                logger.warning(f"File is empty: {full_path}")
                return

            # Extract folder for channel mapping
            # relative_path is like "docs/specs/AGENT_SPECS.md"
            parts = Path(relative_path).parts

            if len(parts) >= 2 and parts[0] == "docs":
                if len(parts) == 2:
                    # File at docs root (e.g., docs/USER_GUIDE.md)
                    folder_name = "root"
                else:
                    # File in subfolder (e.g., docs/specs/AGENT_SPECS.md)
                    folder_name = parts[1]
            else:
                folder_name = "root"

            file_name = full_path.name

            logger.info(f"Processing {file_name} (folder: {folder_name})")

            # Parse markdown
            parsed_doc = self.parser.parse_file(str(full_path), content)

            # Split content into chunks
            chunks = self.splitter.split_with_metadata(
                parsed_doc.content, file_name
            )

            logger.info(f"Split {file_name} into {len(chunks)} chunk(s)")

            # Create embeds
            embeds = self.embed_builder.create_embeds_from_chunks(
                parsed_doc, chunks
            )

            # Post to Discord
            success = await self.bot.post_to_channel(folder_name, embeds)

            if success:
                logger.info(
                    f"Posted {file_name} to Discord ({len(embeds)} message(s))"
                )
            else:
                logger.error(f"Failed to post {file_name} to Discord")

        except Exception as e:
            logger.error(f"Error processing file {relative_path}: {e}", exc_info=True)

    async def check_for_updates(self) -> List[str]:
        """
        Check for updates by comparing local and remote.

        Returns:
            List of modified file paths
        """
        try:
            # Fetch remote
            process = await asyncio.create_subprocess_exec(
                "git", "fetch", "origin",
                cwd=str(self.repo_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await process.communicate()

            # Get diff between local and remote
            process = await asyncio.create_subprocess_exec(
                "git", "diff", "--name-only", "HEAD", "origin/main", "--",
                "docs/",
                cwd=str(self.repo_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, _ = await process.communicate()

            if process.returncode != 0:
                return []

            # Parse output
            files = stdout.decode().strip().split("\n")
            md_files = [f for f in files if f.endswith(".md") and f]

            return md_files

        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
            return []
