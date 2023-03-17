import random
from io import BytesIO

import discord
from discord.ext import commands
from discord import app_commands
from PIL import Image, ImageFont

from bot.utils.champion_utils import (get_champion_key)
from bot.utils.image_utils import (create_team_champion_image,
                                   assemble_origin_images,
                                   create_champion_image_with_name)
from config import Config


class Champions(commands.Cog):

  def __init__(self, bot):
    self.bot = bot
    self.champion_data = bot.champion_data
    self.champion_images = bot.champion_images

  @app_commands.command(name="champions",
                        description="Wygeneruj losowe zdjęcia n championów")
  @app_commands.describe(num_champions="Liczba championów")
  async def champions(self,
                      interaction: discord.Interaction,
                      num_champions: int = 5) -> None:
    try:
      await interaction.response.defer()

      print(f"Generating image with {num_champions} champions...")
      champions = list(self.champion_data.keys())
      selected_champion_keys = random.sample(champions, num_champions)

      images = []
      for champion_key in selected_champion_keys:
        champion_image_path = self.champion_images.get(champion_key)
        champion_name = self.champion_data[champion_key]["name"]
        if champion_image_path:
          images.append(
            create_champion_image_with_name(champion_image_path,
                                            champion_name))

      if not images:
        print(f"No champions found.")
        return

      final_image = assemble_origin_images(images, 10)

      image_buffer = BytesIO()
      final_image.save(image_buffer, format='PNG')
      image_buffer.seek(0)

      image_file = discord.File(image_buffer, filename="champions.png")

      print("Sending result...")
      await interaction.followup.send(file=image_file)

    except Exception as e:
      print(f"An error occurred while processing the command: {str(e)}")
      raise e
