from db import init_db
import discord
from discord.ext import commands
import urllib.parse
import os
from googlesearch import search
from keep_alive import keep_alive
from pvp.view import DuelView
from dotenv import load_dotenv

load_dotenv()


# Récupère le token depuis la variable d'environnement
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Bot connecté en tant que {bot.user}')


@bot.tree.command()
async def artefact(ctx, *, nom: str):
    query = f"site:nwdb.info {nom}"
    try:
        results = list(search(query, num_results=1))
        if results:
            first_url = results[0]
            await ctx.send(f"Voici le lien direct pour **{nom}** :\n{first_url}")
        else:
            await ctx.send(f"Aucun résultat trouvé pour **{nom}**.")
    except Exception as e:
        await ctx.send("Erreur lors de la recherche, veuillez réessayer plus tard.")
        print(f"Erreur Google Search : {e}")
        
@bot.tree.command()
async def duel(interaction: discord.Interaction):
    await interaction.response.send_message("Duel lancé ! Clique sur le bouton pour rejoindre.", 
                                            view=DuelView(interaction.user.id), ephemeral=False)

keep_alive()
init_db()
bot.run(TOKEN)

try:
    bot.run(TOKEN)
except Exception as e:
    print(f"[ERREUR BOT] {e}")
