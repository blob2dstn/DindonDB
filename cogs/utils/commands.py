from googlesearch import search
from discord.ext import commands
from discord import app_commands
import discord
from config import config, save_config

class Utils(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="item", description="Recherche un objet sur NWDB")
    @app_commands.checks.has_permissions(send_messages=True)
    async def item_command(self,interaction: discord.Interaction, nom: str):
        user_roles = [role.id for role in interaction.user.roles]
        if config["allowed_roles"] and not any(role_id in config["allowed_roles"] for role_id in user_roles):
            await interaction.response.send_message("Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
            return

        if not config["allowed_channels"] or str(interaction.channel.id) in config["allowed_channels"]:
            query = f"site:nwdb.info {nom}"
            try:
                result = next(search(query, num_results=1))
                await interaction.response.send_message(f"Résultat pour **{nom}** : {result}")
            except StopIteration:
                await interaction.response.send_message(f"Aucun résultat trouvé pour **{nom}**.")
        else:
            await interaction.response.send_message("Cette commande n'est pas autorisée dans ce salon.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Utils(bot))
    