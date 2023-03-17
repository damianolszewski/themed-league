from discord.ext import commands
from discord import File
from bot.utils.champion_utils import get_champions_by_origin, get_champion_key
from bot.utils.image_utils import create_origin_champion_image, assemble_origin_images
import random
from PIL import Image
from io import BytesIO
from discord import app_commands
import discord
from typing import List
from discord.app_commands import Choice
import json


class Origins(commands.Cog):

  def __init__(self, bot):
    self.bot = bot
    self.origins_data = bot.origins_data
    self.champion_images = bot.champion_images

  @staticmethod
  def join_images(*images, padding=50):
    if not images:
      return Image.new("RGBA", (1, 1), (0, 0, 0, 0))

    total_width = sum(img.width
                      for img in images) + padding * (len(images) - 1)
    max_height = max(img.height for img in images)

    new_image = Image.new("RGBA", (total_width, max_height), (0, 0, 0, 0))

    x_offset = 0
    for img in images:
      new_image.paste(img, (x_offset, 0))
      x_offset += img.width + padding

    return new_image

  def origins_autocomplete() -> List[app_commands.Choice[str]]:
    with open('data/origins.json', 'r') as f:
      origins_data = json.load(f)
    origins = list(origins_data.keys())
    choices = [
      app_commands.Choice(name=origin, value=origin) for origin in origins
    ]
    return choices

  @app_commands.command(name="origin", description="Wygeneruj losową drużynę")
  @app_commands.choices(origin=origins_autocomplete())
  async def origin(self, interaction: discord.Interaction,
                   origin: app_commands.Choice[str]) -> None:

    origin = origin.value
    try:
      print(f"Received team command with origin={origin}")

      champions = get_champions_by_origin(self.origins_data, origin)
      if not champions:
        print(f"No champions found for origin '{origin}'.")
        return

      await interaction.response.defer()

      print("Selecting champions...")
      selected_champions = random.sample(champions, min(5, len(champions)))

      origin_map = {'name': origin, 'champions': selected_champions}
      print("Creating image...")
      origin_image = create_origin_champion_image(origin_map,
                                                  selected_champions,
                                                  self.bot.champion_data,
                                                  self.champion_images)
      image_buffer = BytesIO()
      origin_image.save(image_buffer, format='PNG')
      image_buffer.seek(0)
      image_file = discord.File(image_buffer, filename="team.png")

      await interaction.followup.send(file=image_file)
    except Exception as e:
      print(f"An error occurred while processing the command: {str(e)}")
      raise e

  @app_commands.command(name="origins",
                        description="Wygeneruj losowe narody dla dwóch drużyn")
  @app_commands.describe(num_origins="Liczba narodów na drużynę")
  async def origins(self,
                    interaction: discord.Interaction,
                    num_origins: int = 1) -> None:
    try:
      await interaction.response.defer()
      all_origins = list(self.origins_data.keys())

      origin_group1 = random.sample(all_origins, num_origins)
      origin_group2 = random.sample(
        [origin for origin in all_origins if origin not in origin_group1],
        num_origins)

      origin_images1 = []
      origin_images2 = []

      for origin in origin_group1:
        champions_by_origin = get_champions_by_origin(self.origins_data,
                                                      origin)
        num_champs_to_select = 5
        selected_champions = random.sample(
          champions_by_origin,
          min(num_champs_to_select, len(champions_by_origin)))
        origin_map = {'name': origin, 'champions': self.origins_data[origin]}
        origin_image = create_origin_champion_image(origin_map,
                                                    selected_champions,
                                                    self.bot.champion_data,
                                                    self.champion_images)
        origin_images1.append(origin_image)

      for origin in origin_group2:
        champions_by_origin = get_champions_by_origin(self.origins_data,
                                                      origin)
        num_champs_to_select = 5
        selected_champions = random.sample(
          champions_by_origin,
          min(num_champs_to_select, len(champions_by_origin)))
        origin_map = {'name': origin, 'champions': self.origins_data[origin]}
        origin_image = create_origin_champion_image(origin_map,
                                                    selected_champions,
                                                    self.bot.champion_data,
                                                    self.champion_images)
        origin_images2.append(origin_image)

      img1 = assemble_origin_images(origin_images1, 10, False)
      img2 = assemble_origin_images(origin_images2, 10, False)

      joined_image = self.join_images(img1, img2)

      buffer = BytesIO()
      joined_image.save(buffer, "PNG")
      buffer.seek(0)

      image_file = File(
        buffer,
        filename=
        f"teams_{'_'.join(origin_group1)}_{'_'.join(origin_group2)}.png")
      await interaction.followup.send(file=image_file)
    except Exception as e:
      print(f"An error occurred while processing the command: {str(e)}")
      raise e
