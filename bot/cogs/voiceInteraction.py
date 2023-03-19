import openai
import discord
from discord.ext import commands
from discord import app_commands
from voice_utils import InteractionType, voiceInteraction

class VoiceInteraction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="compliment",
        description="Wyślij komplement losowej osobie na twoim kanale głosowym."
    )
    async def compliment(self, interaction: discord.Interaction):
        await voiceInteraction(InteractionType.COMPLIMENT, interaction)

    @app_commands.command(
        name="joke",
        description="Wyślij żart o losowej osobie na twoim kanale głosowym."
    )
    async def joke(self, interaction: discord.Interaction):
        await voiceInteraction(InteractionType.JOKE, interaction)