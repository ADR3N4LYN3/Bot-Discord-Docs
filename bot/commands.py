"""Slash commands for the Discord Docs Bot."""

import discord
from discord import app_commands
from pathlib import Path
from utils.logger import get_logger
from processors.summary_builder import SummaryBuilder
from utils.channel_manager import ChannelManager

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

            # Initialize managers
            summary_builder = SummaryBuilder(github_repo_url=bot.config.github_repo_url)
            channel_manager = ChannelManager(
                guild=interaction.guild,
                category_name=bot.config.docs_category_name,
                auto_create=bot.config.auto_create_channels,
            )

            # Find all markdown files
            md_files = list(docs_path.glob("**/*.md"))
            total_files = len(md_files)

            if total_files == 0:
                await interaction.followup.send("❌ Aucun fichier markdown trouvé dans le dossier docs/")
                return

            await interaction.followup.send(
                f"📚 Génération de résumés pour {total_files} fichier(s)...\n"
                f"Création/mise à jour des canaux en cours..."
            )

            success_count = 0
            error_count = 0
            created_channels = 0
            updated_channels = 0

            for md_file in md_files:
                try:
                    # Skip README files
                    if md_file.name.upper() == "README.MD":
                        logger.info(f"Skipping README: {md_file.name}")
                        continue

                    logger.info(f"Processing: {md_file.name}")

                    # Read file content
                    content = md_file.read_text(encoding="utf-8")
                    if not content.strip():
                        logger.warning(f"Skipping empty file: {md_file.name}")
                        continue

                    # Build summary
                    summary = summary_builder.build_summary(md_file, content, docs_path)
                    embed = summary_builder.create_summary_embed(summary)

                    # Get or create channel
                    channel = await channel_manager.ensure_channel_exists(md_file.name)
                    if not channel:
                        error_count += 1
                        logger.error(f"Failed to get/create channel for {md_file.name}")
                        continue

                    # Edit existing message or create new one
                    messages = [m async for m in channel.history(limit=1)]
                    if messages and messages[0].author == bot.user:
                        # Edit existing message
                        await messages[0].edit(embed=embed)
                        updated_channels += 1
                        logger.info(f"Updated summary in #{channel.name}")
                    else:
                        # Create new message
                        await channel.send(embed=embed)
                        created_channels += 1
                        logger.info(f"Created summary in #{channel.name}")

                    success_count += 1

                except Exception as e:
                    error_count += 1
                    logger.error(f"Error processing {md_file.name}: {e}", exc_info=True)

            # Send summary
            summary_msg = f"✅ **Refresh terminé !**\n\n"
            summary_msg += f"📄 {success_count}/{total_files} fichier(s) traité(s)\n"
            summary_msg += f"✨ {created_channels} nouveau(x) canal/canaux créé(s)\n"
            summary_msg += f"🔄 {updated_channels} canal/canaux mis à jour\n"
            if error_count > 0:
                summary_msg += f"❌ {error_count} erreur(s)\n"

            await interaction.channel.send(summary_msg)

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
            value="🌐 Webhook GitHub" if bot.config.use_webhook else "📁 File Watcher",
            inline=True
        )

        embed.add_field(
            name="Fichiers surveillés",
            value=f"📄 {len(md_files)} fichiers .md",
            inline=True
        )

        embed.add_field(
            name="Dossier docs",
            value=f"`{docs_path}`",
            inline=False
        )

        embed.add_field(
            name="Configuration",
            value=f"Auto-création: {'✅' if bot.config.auto_create_channels else '❌'}\n"
                  f"Catégorie: {bot.config.docs_category_name}\n"
                  f"GitHub: {'✅ Configuré' if bot.config.github_repo_url else '❌ Non configuré'}",
            inline=False
        )

        # Count channels in DOCS category
        docs_channels = [
            ch for ch in interaction.guild.text_channels
            if ch.category and ch.category.name.upper() == bot.config.docs_category_name.upper()
        ]

        if docs_channels:
            embed.add_field(
                name=f"Canaux dans {bot.config.docs_category_name}",
                value=f"📁 {len(docs_channels)} canal/canaux",
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
