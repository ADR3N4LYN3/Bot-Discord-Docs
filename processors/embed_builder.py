"""Discord embed builder for formatted messages."""

import discord
from datetime import datetime
from typing import List
from processors.markdown_parser import ParsedDocument
from utils.logger import get_logger

logger = get_logger("embed_builder")


class EmbedBuilder:
    """Builds Discord embeds from parsed content."""

    def __init__(self, embed_color: int = 0x5865F2):
        """
        Initialize the embed builder.

        Args:
            embed_color: Color for embeds (default: Discord Blurple)
        """
        self.embed_color = embed_color

    def create_embed(
        self, parsed_doc: ParsedDocument, chunk: dict, file_path: str
    ) -> discord.Embed:
        """
        Create a Discord embed from a content chunk.

        Args:
            parsed_doc: Parsed document object
            chunk: Chunk dict with 'content', 'part', 'total'
            file_path: Path to the file

        Returns:
            Discord Embed object
        """
        # Create embed with title
        embed = discord.Embed(
            title=parsed_doc.title,
            color=self.embed_color,
            timestamp=datetime.utcnow(),
        )

        # Set description (the actual content)
        content = chunk["content"]

        # Discord embed description limit is 4096, but we keep it at 2000 for safety
        if len(content) > 2000:
            content = content[:1997] + "..."

        embed.description = content

        # Add metadata fields if present
        if parsed_doc.metadata:
            for key, value in list(parsed_doc.metadata.items())[:3]:  # Max 3 fields
                embed.add_field(name=key, value=value, inline=True)

        # Add footer with part info and file name
        footer_text = f"📄 {chunk['file_name']}"

        if chunk["total"] > 1:
            footer_text += f" • Partie {chunk['part']}/{chunk['total']}"

        embed.set_footer(text=footer_text)

        logger.debug(
            f"Created embed for {parsed_doc.title} "
            f"(part {chunk['part']}/{chunk['total']})"
        )

        return embed

    def create_embeds_from_chunks(
        self, parsed_doc: ParsedDocument, chunks: List[dict]
    ) -> List[discord.Embed]:
        """
        Create multiple embeds from content chunks.

        Args:
            parsed_doc: Parsed document object
            chunks: List of chunk dicts

        Returns:
            List of Discord Embed objects
        """
        embeds = []

        for chunk in chunks:
            embed = self.create_embed(
                parsed_doc, chunk, chunk["file_name"]
            )
            embeds.append(embed)

        logger.info(
            f"Created {len(embeds)} embed(s) for {parsed_doc.title}"
        )

        return embeds

    def create_simple_embed(
        self, title: str, description: str, color: int = None
    ) -> discord.Embed:
        """
        Create a simple embed with title and description.

        Args:
            title: Embed title
            description: Embed description
            color: Embed color (default: self.embed_color)

        Returns:
            Discord Embed object
        """
        embed = discord.Embed(
            title=title,
            description=description,
            color=color or self.embed_color,
            timestamp=datetime.utcnow(),
        )

        return embed

    def create_error_embed(self, error_message: str) -> discord.Embed:
        """
        Create an error embed.

        Args:
            error_message: Error message to display

        Returns:
            Discord Embed object with error styling
        """
        embed = discord.Embed(
            title="❌ Erreur",
            description=error_message,
            color=0xFF0000,  # Red
            timestamp=datetime.utcnow(),
        )

        return embed

    def create_success_embed(self, success_message: str) -> discord.Embed:
        """
        Create a success embed.

        Args:
            success_message: Success message to display

        Returns:
            Discord Embed object with success styling
        """
        embed = discord.Embed(
            title="✅ Succès",
            description=success_message,
            color=0x00FF00,  # Green
            timestamp=datetime.utcnow(),
        )

        return embed
