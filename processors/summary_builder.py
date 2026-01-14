"""Build compact summaries for documentation files."""

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import discord
from processors.markdown_parser import MarkdownParser
from utils.logger import get_logger

logger = get_logger("summary_builder")


@dataclass
class DocumentSummary:
    """Represents a document summary with key information."""

    title: str
    description: str
    sections: List[str]  # List of h2 section titles
    file_size: str  # "86 KB"
    line_count: int
    code_block_count: int
    github_url: str
    last_modified: datetime
    file_name: str


class SummaryBuilder:
    """Generates compact summaries for documentation files."""

    def __init__(self, github_repo_url: str = ""):
        """
        Initialize the summary builder.

        Args:
            github_repo_url: Base GitHub URL (e.g., "https://github.com/user/repo/blob/main/docs")
        """
        self.parser = MarkdownParser()
        self.github_repo_url = github_repo_url.rstrip("/")

    def build_summary(
        self, file_path: Path, content: str, docs_root: Path
    ) -> DocumentSummary:
        """
        Build a summary from a markdown file.

        Args:
            file_path: Path to the markdown file
            content: File content
            docs_root: Root documentation directory

        Returns:
            DocumentSummary object
        """
        # Parse the document
        parsed = self.parser.parse_file(str(file_path), content)

        # Extract title
        title = parsed.title

        # Extract description (first paragraph after title)
        description = self._extract_description(content)

        # Extract section titles (h2 headers only)
        sections = self.parser.extract_sections(content)
        section_titles = [section[0] for section in sections]

        # Calculate stats
        file_size = self._format_file_size(len(content.encode("utf-8")))
        line_count = len(content.split("\n"))
        code_block_count = len(parsed.code_blocks)

        # Build GitHub URL
        relative_path = file_path.relative_to(docs_root)
        github_url = self._build_github_url(relative_path)

        # Get last modified time
        last_modified = datetime.fromtimestamp(file_path.stat().st_mtime)

        logger.debug(
            f"Built summary for {file_path.name}: "
            f"{len(section_titles)} sections, "
            f"{code_block_count} code blocks"
        )

        return DocumentSummary(
            title=title,
            description=description,
            sections=section_titles,
            file_size=file_size,
            line_count=line_count,
            code_block_count=code_block_count,
            github_url=github_url,
            last_modified=last_modified,
            file_name=file_path.name,
        )

    def _extract_description(self, content: str) -> str:
        """
        Extract the first paragraph after the title as description.

        Args:
            content: Markdown content

        Returns:
            Description text (max 200 chars)
        """
        lines = content.split("\n")
        description_lines = []
        found_title = False
        in_description = False

        for line in lines:
            stripped = line.strip()

            # Skip until we find the title
            if not found_title:
                if stripped.startswith("# "):
                    found_title = True
                continue

            # Skip empty lines and blockquotes after title
            if not stripped or stripped.startswith(">"):
                continue

            # Skip h2 headers
            if stripped.startswith("## "):
                break

            # Found content
            in_description = True
            description_lines.append(stripped)

            # Stop at first paragraph break or after ~200 chars
            if not stripped or len(" ".join(description_lines)) > 200:
                break

        description = " ".join(description_lines).strip()

        # Truncate to 200 chars max
        if len(description) > 200:
            description = description[:197] + "..."

        return description or "Pas de description disponible."

    def _format_file_size(self, size_bytes: int) -> str:
        """
        Format file size in human-readable format.

        Args:
            size_bytes: Size in bytes

        Returns:
            Formatted size (e.g., "86 KB", "1.2 MB")
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.0f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"

    def _build_github_url(self, relative_path: Path) -> str:
        """
        Build GitHub URL for a file.

        Args:
            relative_path: Path relative to docs root

        Returns:
            Full GitHub URL or empty string if no base URL configured
        """
        if not self.github_repo_url:
            return ""

        # Convert Windows path to URL format
        path_str = str(relative_path).replace("\\", "/")
        return f"{self.github_repo_url}/{path_str}"

    def create_summary_embed(self, summary: DocumentSummary) -> discord.Embed:
        """
        Create a compact Discord embed for the summary.

        Args:
            summary: DocumentSummary object

        Returns:
            Discord Embed
        """
        # Create embed with blurple color
        embed = discord.Embed(
            title=f"📄 {summary.file_name}",
            description=summary.description,
            color=0x5865F2,  # Discord blurple
            timestamp=summary.last_modified,
        )

        # Add separator
        embed.add_field(
            name="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            value="",
            inline=False,
        )

        # Add sections list (if any)
        if summary.sections:
            # Limit to first 15 sections for readability
            sections_to_show = summary.sections[:15]
            sections_text = "\n".join(f"• {section}" for section in sections_to_show)

            if len(summary.sections) > 15:
                sections_text += f"\n• ... et {len(summary.sections) - 15} autres"

            embed.add_field(
                name=f"📑 Sections ({len(summary.sections)}):",
                value=sections_text,
                inline=False,
            )

        # Add stats
        stats_text = (
            f"📊 {summary.file_size} • "
            f"{summary.line_count:,} lignes • "
            f"{summary.code_block_count} bloc{'s' if summary.code_block_count > 1 else ''} de code"
        )
        embed.add_field(name="", value=stats_text, inline=False)

        # Add GitHub link if available
        if summary.github_url:
            embed.add_field(
                name="",
                value=f"🔗 [Voir sur GitHub]({summary.github_url})",
                inline=False,
            )

        # Add separator
        embed.add_field(
            name="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            value="",
            inline=False,
        )

        # Footer with last update time
        embed.set_footer(text=f"Dernière mise à jour")

        return embed
