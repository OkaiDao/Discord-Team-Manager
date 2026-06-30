import discord
from discord import app_commands
from discord.ext import commands
from src.views import SignupView

class SetupCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setup_signup", description="Post the signup panel.")
    async def setup_signup(self, interaction: discord.Interaction):
        view = SignupView()
        await interaction.response.send_message("Team signup panel:", view=view)
