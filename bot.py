import json
import asyncio
import discord
from discord.ext import commands
from src.views import SignupView
from src.commands import SetupCommands

with open("config.json") as f:
    cfg = json.load(f)

bot = commands.Bot(
    command_prefix="!", 
    intents=discord.Intents.all(),
    application_id="1520289815269085235"
)

@bot.event
async def on_ready():
    bot.add_view(SignupView())
    await bot.add_cog(SetupCommands(bot))
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

bot.run(cfg["token"])
