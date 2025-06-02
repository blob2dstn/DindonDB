
from discord.ext import commands
from discord import app_commands
import discord
from config import config, save_config

class Moderation(commands.Cog):
    """
    Cog pour gérer les commandes liées au PvP
    """

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setup_role", description="Ajoute un rôle autorisé à utiliser les commandes")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_role_command(self,interaction: discord.Interaction, role: discord.Role):
        if role.id not in config["allowed_roles"]:
            config["allowed_roles"].append(role.id)
            save_config(config)
            await interaction.response.send_message(f"Rôle **{role.name}** ajouté aux autorisations.")
        else:
            await interaction.response.send_message(f"Le rôle **{role.name}** est déjà autorisé.")
            
    @app_commands.command(name="setup_channels", description="Configure les salons autorisés pour les commandes")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(channels="Salons autorisés, séparés par des virgules (IDs)")
    async def setup_channels_command(self,interaction: discord.Interaction, channels: str):
        ids = [id.strip() for id in channels.split(",") if id.strip().isdigit()]
        config["allowed_channels"] = ids
        save_config(config)
        await interaction.response.send_message(f"Salons autorisés mis à jour : {', '.join(ids)}")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
    