"""Slash commands for the Discord Docs Bot."""

import discord
from discord import app_commands
from pathlib import Path
from utils.logger import get_logger
from processors.markdown_parser import MarkdownParser
from processors.message_splitter import MessageSplitter
from processors.embed_builder import EmbedBuilder

logger = get_logger("bot.commands")


def setup_commands(bot):
    """
    Setup slash commands for the bot.

    Args:
        bot: DocsBot instance
    """

    @bot.tree.command(
        name="refresh",
        description="Republier toute la documentation dans les canaux Discord"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def refresh(interaction: discord.Interaction):
        """Republish all documentation to Discord channels."""
        await interaction.response.defer(thinking=True)

        try:
            docs_path = bot.config.docs_path
            parser = MarkdownParser()
            splitter = MessageSplitter(max_length=bot.config.max_message_length - 100)
            embed_builder = EmbedBuilder(embed_color=bot.config.embed_color)

            # Find all markdown files
            md_files = list(docs_path.glob("**/*.md"))
            total_files = len(md_files)

            if total_files == 0:
                await interaction.followup.send("❌ Aucun fichier markdown trouvé dans le dossier docs/")
                return

            await interaction.followup.send(
                f"📚 Publication de {total_files} fichier(s) en cours...\n"
                f"Cela peut prendre quelques minutes."
            )

            success_count = 0
            error_count = 0

            for md_file in md_files:
                try:
                    # Determine folder for channel mapping
                    relative = md_file.relative_to(docs_path)
                    if len(relative.parts) == 1:
                        folder_name = "root"
                    else:
                        folder_name = relative.parts[0]

                    logger.info(f"Processing: {md_file.name} → folder '{folder_name}' (relative: {relative})")

                    # Read and parse file
                    content = md_file.read_text(encoding="utf-8")
                    if not content.strip():
                        continue

                    parsed_doc = parser.parse_file(str(md_file), content)
                    chunks = splitter.split_with_metadata(parsed_doc.content, md_file.name)
                    embeds = embed_builder.create_embeds_from_chunks(parsed_doc, chunks)

                    # Post to channel
                    success = await bot.post_to_channel(folder_name, embeds)

                    if success:
                        success_count += 1
                        logger.info(f"Published {md_file.name} to {folder_name}")
                    else:
                        error_count += 1
                        logger.error(f"Failed to publish {md_file.name}")

                except Exception as e:
                    error_count += 1
                    logger.error(f"Error processing {md_file}: {e}")

            # Send summary
            summary = f"✅ Publication terminée !\n\n"
            summary += f"📄 **{success_count}** fichier(s) publié(s)\n"
            if error_count > 0:
                summary += f"❌ **{error_count}** erreur(s)\n"

            await interaction.channel.send(summary)

        except Exception as e:
            logger.error(f"Error in refresh command: {e}", exc_info=True)
            await interaction.followup.send(f"❌ Erreur: {str(e)}")

    @bot.tree.command(
        name="status",
        description="Afficher le statut du bot"
    )
    async def status(interaction: discord.Interaction):
        """Show bot status."""
        docs_path = bot.config.docs_path
        md_files = list(docs_path.glob("**/*.md")) if docs_path.exists() else []

        embed = discord.Embed(
            title="📊 Statut du Bot",
            color=bot.config.embed_color
        )

        embed.add_field(
            name="Mode",
            value="Webhook" if bot.config.use_webhook else "File Watcher",
            inline=True
        )

        embed.add_field(
            name="Fichiers surveillés",
            value=f"{len(md_files)} fichiers .md",
            inline=True
        )

        embed.add_field(
            name="Dossier docs",
            value=f"`{docs_path}`",
            inline=False
        )

        # Channel status
        if bot.channel_resolver:
            channels = bot.channel_resolver.verify_all_channels_exist()
            channel_status = "\n".join([
                f"{'✅' if exists else '❌'} #{name}"
                for name, exists in channels.items()
            ])
            embed.add_field(
                name="Canaux",
                value=channel_status,
                inline=False
            )

        await interaction.response.send_message(embed=embed)

    @refresh.error
    async def refresh_error(interaction: discord.Interaction, error):
        """Handle refresh command errors."""
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ Vous devez être administrateur pour utiliser cette commande.",
                ephemeral=True
            )
        else:
            logger.error(f"Refresh command error: {error}")
            await interaction.response.send_message(
                f"❌ Erreur: {str(error)}",
                ephemeral=True
            )

    logger.info("Slash commands registered")
