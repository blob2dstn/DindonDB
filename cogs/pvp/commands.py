from cogs.pvp.views import PvpMenuView, NewDuelView
from cogs.pvp import db
from discord.ext import commands
from discord import app_commands
import discord
from config import config, save_config

class Pvp(commands.Cog):
    """
    Cog pour gérer les commandes liées au PvP
    """

    def __init__(self, bot):
        self.bot = bot
        db.init_db()

    @app_commands.command(name="pvp-duel", description="Créer un nouveau duel.")
    # @app_commands.checks.has_any_role(*(int(r) for r in config["allowed_roles"]))
    async def duel(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Apparemment <@{interaction.user.id}> veut se battre !\nQui veut se mesurer à lui ?", 
                                            view=NewDuelView(interaction.user.id), ephemeral=False)
        
    @app_commands.command(name="pvp-menu", description="Menu PvP.")
    # @app_commands.checks.has_any_role(*(int(r) for r in config["allowed_roles"]))
    async def duelList(self, interaction: discord.Interaction):
        await interaction.response.send_message( 
                                            view=PvpMenuView(interaction.user.id), ephemeral=False)
    


async def setup(bot):
    await bot.add_cog(Pvp(bot))