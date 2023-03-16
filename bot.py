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
  width, height = 120 * len(champions), 120
  team_image = Image.new("RGBA", (width, height), (255, 255, 255, 0))

  for i, champ in enumerate(champions):
    icon_url = f"https://ddragon.leagueoflegends.com/cdn/11.18.1/img/champion/{champ}.png"
    response = requests.get(icon_url)
    champ_image = Image.open(io.BytesIO(response.content))
    champ_image = champ_image.resize((100, 100), Image.ANTIALIAS)

    x, y = i * 120, 0
    team_image.paste(champ_image, (x, y))

    draw = ImageDraw.Draw(team_image)
    # Change the font file path to an appropriate one on your system
    font = ImageFont.load_default()
    draw.text((x, y + 100), champ, (0, 0, 0), font=font)

  img_byte_arr = io.BytesIO()
  team_image.save(img_byte_arr, format='PNG')
  img_byte_arr.seek(0)

  return img_byte_arr


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
