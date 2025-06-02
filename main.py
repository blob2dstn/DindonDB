from db import init_db
import discord
from discord import app_commands
from discord.ext import commands
from googlesearch import search
import json
import os
from keep_alive import keep_alive
from pvp.view import DuelView
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

CONFIG_FILE = "config.json"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

config = load_config()

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Bot connecté en tant que {bot.user}')

@tree.command(name="item", description="Recherche un objet sur NWDB")
@app_commands.checks.has_permissions(send_messages=True)
async def item_command(interaction: discord.Interaction, nom: str):
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

@tree.command(name="setup_role", description="Ajoute un rôle autorisé à utiliser les commandes")
@app_commands.checks.has_permissions(administrator=True)
async def setup_role_command(interaction: discord.Interaction, role: discord.Role):
    if role.id not in config["allowed_roles"]:
        config["allowed_roles"].append(role.id)
        save_config(config)
        await interaction.response.send_message(f"Rôle **{role.name}** ajouté aux autorisations.")
    else:
        await interaction.response.send_message(f"Le rôle **{role.name}** est déjà autorisé.")

@tree.command(name="setup_channels", description="Configure les salons autorisés pour les commandes")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(channels="Salons autorisés, séparés par des virgules (IDs)")
async def setup_channels_command(interaction: discord.Interaction, channels: str):
    ids = [id.strip() for id in channels.split(",") if id.strip().isdigit()]
    config["allowed_channels"] = ids
    save_config(config)
    await interaction.response.send_message(f"Salons autorisés mis à jour : {', '.join(ids)}")

keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
