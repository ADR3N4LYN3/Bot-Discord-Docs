"""Markdown parsing and conversion for Discord."""

import re
from dataclasses import dataclass
from typing import List, Optional
from utils.logger import get_logger

logger = get_logger("markdown_parser")


@dataclass
class CodeBlock:
    """Represents a code block in markdown."""

    language: str
    content: str
    start_pos: int
    end_pos: int


@dataclass
class ParsedDocument:
    """Represents a parsed markdown document."""

    title: str
    content: str
    code_blocks: List[CodeBlock]
    metadata: dict


class MarkdownParser:
    """Parser for markdown documents."""

    def __init__(self):
        """Initialize the markdown parser."""
        self.code_block_pattern = re.compile(
            r"```(\w*)\n(.*?)```", re.DOTALL | re.MULTILINE
        )

    def parse_file(self, file_path: str, content: str) -> ParsedDocument:
        """
        Parse a markdown file.

        Args:
            file_path: Path to the file
            content: File content

        Returns:
            ParsedDocument object
        """
        # Extract title (first h1 heading)
        title = self._extract_title(content, file_path)

        # Extract code blocks
        code_blocks = self._extract_code_blocks(content)

        # Extract metadata from blockquotes at start
        metadata = self._extract_metadata(content)

        logger.debug(
            f"Parsed {file_path}: title='{title}', "
            f"{len(code_blocks)} code blocks, "
            f"{len(metadata)} metadata items"
        )

        return ParsedDocument(
            title=title,
            content=content,
            code_blocks=code_blocks,
            metadata=metadata,
        )

    def _extract_title(self, content: str, file_path: str) -> str:
        """Extract the first h1 heading as title."""
        match = re.search(r"^#\s+(.+?)$", content, re.MULTILINE)

        if match:
            return match.group(1).strip()
        else:
            # Fallback to filename
            import os

            return os.path.basename(file_path).replace(".md", "")

    def _extract_code_blocks(self, content: str) -> List[CodeBlock]:
        """Extract all code blocks from the content."""
        code_blocks = []

        for match in self.code_block_pattern.finditer(content):
            language = match.group(1) or "text"
            code_content = match.group(2)
            start_pos = match.start()
            end_pos = match.end()

            code_blocks.append(
                CodeBlock(
                    language=language,
                    content=code_content,
                    start_pos=start_pos,
                    end_pos=end_pos,
                )
            )

        return code_blocks

    def _extract_metadata(self, content: str) -> dict:
        """
        Extract metadata from blockquotes at the start of the file.

        Example:
            > **Statut** : ✅ Implémenté
            > **Date** : 2026-01-02
        """
        metadata = {}

        # Look for blockquotes at the start (after title)
        lines = content.split("\n")
        in_blockquote = False

        for line in lines:
            stripped = line.strip()

            # Skip empty lines and title
            if not stripped or stripped.startswith("#"):
                continue

            # Check if this is a blockquote
            if stripped.startswith(">"):
                in_blockquote = True
                # Try to parse key: value
                match = re.search(r">\s*\*\*(.+?)\*\*\s*[:\-]\s*(.+)", stripped)
                if match:
                    key = match.group(1).strip()
                    value = match.group(2).strip()
                    metadata[key] = value
            elif in_blockquote:
                # End of blockquote section
                break

        return metadata

    def convert_to_discord(self, content: str) -> str:
        """
        Convert markdown to Discord-compatible format.

        Discord supports most markdown, but we need to be careful with:
        - Tables (keep as-is, Discord has partial support)
        - Code blocks (preserve with language)
        - Links (keep as-is)
        - Emojis (keep as-is)

        Args:
            content: Markdown content

        Returns:
            Discord-compatible markdown
        """
        # Discord markdown is largely compatible with standard markdown
        # We just need to ensure code blocks are properly formatted

        # No conversion needed for now - Discord handles most markdown well
        return content

    def extract_sections(self, content: str) -> List[tuple[str, str]]:
        """
        Extract sections (by h2 headers) from content.

        Args:
            content: Markdown content

        Returns:
            List of (section_title, section_content) tuples
        """
        sections = []
        lines = content.split("\n")

        current_section_title = None
        current_section_lines = []

        for line in lines:
            # Check if this is an h2 heading
            if line.startswith("## "):
                # Save previous section if exists
                if current_section_title:
                    sections.append(
                        (current_section_title, "\n".join(current_section_lines))
                    )

                # Start new section
                current_section_title = line[3:].strip()
                current_section_lines = []
            else:
                if current_section_title is not None:
                    current_section_lines.append(line)

        # Save last section
        if current_section_title:
            sections.append(
                (current_section_title, "\n".join(current_section_lines))
            )

        return sections
