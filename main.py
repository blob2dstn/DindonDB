import discord
from discord import app_commands
from discord.ext import commands
import urllib.parse
import json
import os

from keep_alive import keep_alive

# Chargement de la configuration
CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
config = load_config()

@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🔁 {len(synced)} commandes slash synchronisées.")
    except Exception as e:
        print(f"Erreur de sync : {e}")

# Commande /item
@bot.tree.command(name="item", description="Recherche un objet ou artefact dans NWDB")
@app_commands.describe(nom="Nom de l'objet ou artefact à rechercher")
async def item(interaction: discord.Interaction, nom: str):
    config = load_config()
    allowed_roles = config.get("allowed_role_ids", [])
    allowed_channels = config.get("allowed_channel_ids", [])

    # Vérifie si le salon est autorisé
    if allowed_channels and interaction.channel_id not in allowed_channels:
        await interaction.response.send_message("⛔ Ce salon n'est pas autorisé à utiliser cette commande.", ephemeral=True)
        return

    # Vérifie si l'utilisateur a le rôle requis
    if allowed_roles:
        user_roles = [role.id for role in interaction.user.roles]
        if not any(role_id in user_roles for role_id in allowed_roles):
            await interaction.response.send_message("⛔ Tu n'as pas le rôle requis pour utiliser cette commande.", ephemeral=True)
            return

    query = urllib.parse.quote(f"site:nwdb.info {nom}")
    url = f"https://www.google.com/search?q={query}"
    await interaction.response.send_message(f"🔎 Résultat pour **{nom}** :\n{url}")

# Commande /setup groupée
setup_group = app_commands.Group(name="setup", description="Configurer le bot")

@setup_group.command(name="role", description="Définit le rôle autorisé pour les commandes du bot")
@app_commands.describe(role="Rôle autorisé")
async def setup_role(interaction: discord.Interaction, role: discord.Role):
    config = load_config()
    config["allowed_role_ids"] = [role.id]
    save_config(config)
    await interaction.response.send_message(f"✅ Le rôle autorisé est maintenant : {role.name}")

@setup_group.command(name="channel", description="Ajoute un salon autorisé")
@app_commands.describe(salon="Salon autorisé")
async def setup_channel(interaction: discord.Interaction, salon: discord.TextChannel):
    config = load_config()
    allowed_channels = config.get("allowed_channel_ids", [])
    if salon.id not in allowed_channels:
        allowed_channels.append(salon.id)
        config["allowed_channel_ids"] = allowed_channels
        save_config(config)
        await interaction.response.send_message(f"✅ Salon autorisé ajouté : {salon.mention}")
    else:
        await interaction.response.send_message(f"ℹ️ Le salon {salon.mention} est déjà autorisé.")

bot.tree.add_command(setup_group)

# Démarrage serveur keep_alive + bot
keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
