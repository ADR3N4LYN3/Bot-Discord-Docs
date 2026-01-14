"""Git operations handler for pulling changes and detecting diffs."""

import asyncio
import subprocess
from pathlib import Path
from typing import List
from utils.logger import get_logger
from processors.summary_builder import SummaryBuilder
from utils.channel_manager import ChannelManager

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

        # Initialize summary builder
        self.summary_builder = SummaryBuilder(github_repo_url=config.github_repo_url)
        self.channel_manager = None  # Will be initialized when needed

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
        Process a single modified file and update its Discord channel.

        Args:
            relative_path: Path relative to repo root (e.g., "docs/specs/AGENT_SPECS.md")
        """
        try:
            full_path = self.repo_path / relative_path

            if not full_path.exists():
                logger.warning(f"File not found after pull: {full_path}")
                return

            # Skip README files
            if full_path.name.upper() == "README.MD":
                logger.info(f"Skipping README: {full_path.name}")
                return

            # Read file content
            content = full_path.read_text(encoding="utf-8")

            if not content.strip():
                logger.warning(f"File is empty: {full_path}")
                return

            file_name = full_path.name
            logger.info(f"Processing update for {file_name}")

            # Initialize channel manager if needed
            if not self.channel_manager:
                guild = self.bot.get_target_guild()
                if not guild:
                    logger.error("Cannot process file: guild not found")
                    return

                self.channel_manager = ChannelManager(
                    guild=guild,
                    category_id=self.config.docs_category_id,
                    auto_create=self.config.auto_create_channels,
                )

            # Build summary
            docs_path = self.config.docs_path
            summary = self.summary_builder.build_summary(full_path, content, docs_path)
            embed = self.summary_builder.create_summary_embed(summary)

            # Get or create channel
            channel = await self.channel_manager.ensure_channel_exists(file_name)
            if not channel:
                logger.error(f"Failed to get/create channel for {file_name}")
                return

            # Edit existing message or create new one
            messages = [m async for m in channel.history(limit=1)]
            if messages and messages[0].author == self.bot.user:
                # Edit existing message
                await messages[0].edit(embed=embed)
                logger.info(f"Updated summary in #{channel.name}")
            else:
                # Create new message
                await channel.send(embed=embed)
                logger.info(f"Created summary in #{channel.name}")

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
