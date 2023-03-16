import os
import random
import discord
from discord.ext import commands
from discord import Embed
import json
import requests
import io
from PIL import Image, ImageDraw, ImageFont

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

CHANNEL_ID = 701417126392627341
RIOT_API_KEY = os.getenv("RIOT_API_KEY")

with open("origins.json", "r") as f:
  origins_data = json.load(f)


def get_champions_by_origin(origin: str):
  champions = []
  for origin_entry in origins_data:
    print(origin_entry)
    if origin_entry.lower() == origin.lower():
      champions = origins_data[origin_entry]
      break
  return champions


@bot.event
async def on_ready():
  print(f"Logged in as {bot.user.name}")
  print("------")


async def create_team_image(champions):
    images = []
    for champ in champions:
        icon_url = f"https://ddragon.leagueoflegends.com/cdn/11.18.1/img/champion/{champ}.png"
        response = requests.get(icon_url)
        image = Image.open(BytesIO(response.content)).convert("RGBA")
        images.append(image)

    total_width = sum(image.width for image in images)
    max_height = max(image.height for image in images)

    team_image = Image.new("RGBA", (total_width, max_height + 40), (0, 0, 0, 0))
    font = ImageFont.truetype("couture-bld.otf", 24)  # Change the font and size

    x_offset = 0
    for i, image in enumerate(images):
        team_image.paste(image, (x_offset, 40))
        draw = ImageDraw.Draw(team_image)
        text = champions[i]
        text_width, text_height = draw.textsize(text, font=font)
        text_x = x_offset + (image.width - text_width) // 2
        draw.text((text_x, 0), text, font=font, fill=(255, 255, 255))  # Change the text color to white
        x_offset += image.width

    buffer = BytesIO()
    team_image.save(buffer, "PNG")
    buffer.seek(0)
    return buffer

@bot.command(name="team")
async def team(ctx):
  origin = ctx.message.content.split(" ")[1]
  print(f"Received team command with origin={origin}")

  champions = get_champions_by_origin(origin)
  if not champions:
    await ctx.send(f"No champions found for origin '{origin}'.")
    return

  selected_champions = random.sample(champions, min(5, len(champions)))

  team_image = await create_team_image(selected_champions)

  await ctx.send(f"Here is your {origin} team:",
                 file=discord.File(team_image, "team.png"))


bot.run(os.getenv("DISCORD_TOKEN"))

bot.run(os.getenv("DISCORD_TOKEN"))
