import random
from io import BytesIO

import discord
from discord.ext import commands
from discord import app_commands
from PIL import Image, ImageDraw, ImageFont

from bot.utils.champion_utils import (get_champion_key)
from bot.utils.image_utils import (create_team_champion_image,
                                   assemble_origin_images)
from config import Config


class Teams(commands.Cog):

  def __init__(self, bot):
    self.bot = bot
    self.champion_data = bot.champion_data
    self.champion_images = bot.champion_images

  @app_commands.command(name="team", description="Wygeneruj losową drużynę")
  async def team(self, interaction: discord.Interaction) -> None:
    try:
      champions = list(self.champion_data.keys())
      selected_champion_keys = random.sample(champions, 5)

      await interaction.response.defer()

      print("Generating image...")
      team_image = create_team_champion_image(selected_champion_keys,
                                              self.champion_data,
                                              self.champion_images)
      image_buffer = BytesIO()
      team_image.save(image_buffer, format='PNG')
      image_buffer.seek(0)

      image_file = discord.File(image_buffer, filename="team.png")

      print("Sending result...")
      await interaction.followup.send(file=image_file)
    except Exception as e:
      print(f"An error occurred while processing the command: {str(e)}")
      raise e

  @app_commands.command(name="teams",
                        description="Wygeneruj dwie losowe drużyny")
  async def teams(self, interaction: discord.Interaction) -> None:
    try:
      champions = list(self.champion_data.keys())
      selected_champions = random.sample(champions, 10)
      team1_champion_keys = selected_champions[:5]
      team2_champion_keys = selected_champions[5:]

      await interaction.response.defer()

      team1_image = create_team_champion_image(team1_champion_keys,
                                               self.champion_data,
                                               self.champion_images,
                                               "Team Blue")
      team2_image = create_team_champion_image(team2_champion_keys,
                                               self.champion_data,
                                               self.champion_images,
                                               "Team Red")

      image_buffer = BytesIO()
      team1_image.save(image_buffer, format='PNG')
      image_buffer.seek(0)
      team1_file = discord.File(image_buffer, filename="team1.png")

      image_buffer = BytesIO()
      team2_image.save(image_buffer, format='PNG')
      image_buffer.seek(0)
      team2_file = discord.File(image_buffer, filename="team2.png")

      final_image = assemble_origin_images([team1_image, team2_image], 30)

      image_buffer = BytesIO()
      final_image.save(image_buffer, format='PNG')
      image_buffer.seek(0)

      image_file = discord.File(image_buffer, filename="teams.png")

      await interaction.followup.send(file=image_file)
    except Exception as e:
      print(f"An error occurred while processing the command: {str(e)}")
      raise e
