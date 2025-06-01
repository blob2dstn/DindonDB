import discord
from discord.ext import commands
from discord import app_commands
import os, json
from googlesearch import search
from keep_alive import keep_alive

TOKEN = os.getenv("DISCORD_TOKEN")
CONFIG_FILE = "config.json"

intents = discord.Intents.default()
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)

@bot.event
async def on_ready():
    await bot.wait_until_ready()
    try:
        await bot.tree.sync()
        print(f"✅ Bot connecté en tant que {bot.user}")
    except Exception as e:
        print("Erreur de synchronisation :", e)

# Groupe de commandes /setup
setup_group = app_commands.Group(name="setup", description="Configurer les autorisations du bot")

@setup_group.command(name="role", description="Définit le rôle autorisé à utiliser /artefact")
@app_commands.checks.has_permissions(administrator=True)
async def setup_role(interaction: discord.Interaction, role: discord.Role):
    config = load_config()
    config["allowed_role_id"] = role.id
    save_config(config)
    await interaction.response.send_message(f"✅ Rôle autorisé : **{role.name}**", ephemeral=True)

@setup_group.command(name="channels", description="Définit les salons où /artefact est autorisé")
@app_commands.checks.has_permissions(administrator=True)
async def setup_channels(interaction: discord.Interaction, channels: list[discord.TextChannel]):
    config = load_config()
    config["allowed_channel_ids"] = [c.id for c in channels]
    save_config(config)
    names = ", ".join(f"#{c.name}" for c in channels)
    await interaction.response.send_message(f"✅ Salons autorisés : {names}", ephemeral=True)

bot.tree.add_command(setup_group)

# Commande principale : /item
@bot.tree.command(name="item", description="Recherche un item sur NWDB")
@app_commands.describe(nom="Nom de l'item à chercher")
async def item(interaction: discord.Interaction, nom: str):
    config = load_config()
    role_id = config.get("allowed_role_id")
    allowed_channels = config.get("allowed_channel_ids", [])

    if role_id is None or role_id not in [role.id for role in interaction.user.roles]:
        await interaction.response.send_message("❌ Tu n’as pas le rôle requis.", ephemeral=True)
        return

    if allowed_channels and interaction.channel.id not in allowed_channels:
        await interaction.response.send_message("❌ Ce salon n’est pas autorisé.", ephemeral=True)
        return

    query = f"site:nwdb.info {nom}"
    try:
        result = next(search(query, num=1))
        await interaction.response.send_message(f"🔎 Résultat pour **{nom}** :\n{result}")
    except Exception:
        await interaction.response.send_message("❌ Aucun résultat trouvé.", ephemeral=True)

# Commande admin : /status
@bot.tree.command(name="status", description="Affiche la configuration actuelle du bot")
@app_commands.checks.has_permissions(administrator=True)
async def status(interaction: discord.Interaction):
    config = load_config()
    role_id = config.get("allowed_role_id")
    channel_ids = config.get("allowed_channel_ids", [])

    guild = interaction.guild
    role = guild.get_role(role_id) if role_id else None
    channels = [guild.get_channel(cid) for cid in channel_ids if guild.get_channel(cid)]

    role_display = f"<@&{role.id}>" if role else "*Non défini*"
    channels_display = "\n".join(f"- <#{c.id}>" for c in channels) if channels else "*Aucun salon défini*"

    embed = discord.Embed(
        title="Configuration du Bot",
        color=discord.Color.green()
    )
    embed.add_field(name="Rôle autorisé", value=role_display, inline=False)
    embed.add_field(name="Salons autorisés", value=channels_display, inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)

# Gestion des erreurs
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("🔒 Tu dois être administrateur.", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Une erreur est survenue.", ephemeral=True)
        print(error)

# Lancer le bot
keep_alive()
bot.run(TOKEN)
