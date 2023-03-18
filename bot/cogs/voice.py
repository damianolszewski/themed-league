import random
from io import BytesIO

import discord
from discord.ext import commands
from discord import app_commands
from PIL import Image, ImageDraw, ImageFont

from bot.utils.champion_utils import get_champion_key
from bot.utils.image_utils import create_champion_image_with_name
from bot.utils.voice_utils import get_voice_channel_members

import requests

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.champion_data = bot.champion_data
        self.champion_images = bot.champion_images

    @app_commands.command(
        name="voice",
        description="Przypisuje losową postać do każdego użytkownika discord'a z aktualnego kanału głosowego."
    )
    async def voice(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer()

            if not interaction.user.voice:
                await interaction.followup.send(
                    "Musisz być na kanale głosowym!"
                )
                return

            members = get_voice_channel_members(interaction)

            if not members:
                await interaction.followup.send("Nie ma nikogo na kanale głosowym!")
                return

            champions = {}

            for member in members:
                champion_name = random.choice(list(self.champion_data.keys()))
                champions[member] = champion_name

            final_image = self.create_voice_image(members, champions, self.champion_data, self.champion_images)

            await self.send_voice_image(interaction, final_image)

        except Exception as e:
            print(f"An error occurred while processing the command: {str(e)}")
            raise e


    def create_voice_image(self, members, champions, champion_data, champion_images):
        # Calculate the size of each cell
        cell_width = 128
        cell_height = 150
        padding = 5

        # Calculate the size of the final image
        n_members = len(members)
        final_width = cell_width * (n_members + 1) + padding * (n_members + 2)
        final_height = cell_height * 2 + padding * 8
        final_image = Image.new("RGBA", (final_width, final_height), (0, 0, 0, 0))

        # Draw the user names and images in the first and second rows
        font = ImageFont.truetype("data/font.ttf", 18)
        text_color = (255, 255, 255)
        draw = ImageDraw.Draw(final_image)

        for i, member in enumerate(members):
            member_name = member.display_name
            x = (cell_width + padding) * i + padding
            y = padding
            draw.text((x, y), member_name, fill=text_color, font=font)

            avatar_url = member.avatar.url
            response = requests.get(avatar_url)
            avatar_image = Image.open(BytesIO(response.content)).convert("RGBA")
            avatar_image = avatar_image.resize((128, 128))

            x = (cell_width + padding) * i + padding
            y = 30 + padding * 2
            final_image.paste(avatar_image, (x, y))

            # Select random champions for each member and draw the champion images and names in the third and fourth rows
            champion_name = champions[member]
            champion_key = get_champion_key(champion_data, champion_name)
            champion_image_url = champion_images.get(champion_key)
            if champion_image_url:
              champion_image = create_champion_image_with_name(champion_image_url, champion_name)

              x = (cell_width + padding) * i + padding
              y = cell_height + padding * 4
              final_image.paste(champion_image, (x, y))

              draw.textsize(champion_name, font=font)

        return final_image


    async def send_voice_image(self, interaction, final_image):
      # Save the final image to a buffer and send it as a message
      image_buffer = BytesIO()
      final_image.save(image_buffer, format='PNG')
      image_buffer.seek(0)

      image_file = discord.File(image_buffer, filename="voice.png")
      await interaction.followup.send(file=image_file)