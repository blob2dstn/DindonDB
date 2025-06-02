import discord
from discord import app_commands
from discord.ext import commands
from googlesearch import search
import json
import os
from keep_alive import keep_alive
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

@bot.event
async def on_ready():
    await load_cogs()
    await bot.tree.sync()
    print(f"✅ Connecté en tant que {bot.user}:{bot.user.id} (slash commands synchronisées)")
    print("Commandes slash :")
    for cmd in await bot.tree.fetch_commands():
        print(f"- /{cmd.name}: {cmd.description}")

async def load_cogs():
    for extension in ['cogs.moderation.commands', 'cogs.utils.commands', 'cogs.pvp.commands']:
            await bot.load_extension(extension)
            print(f"Extension {extension} chargée.")


keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
