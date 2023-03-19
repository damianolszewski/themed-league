import os
import discord
from discord.ext import commands
from discord import app_commands
from discord import Interaction
from discord.ext.commands import Greedy, Context
from typing import Literal, Optional
from bot.cogs import origins, teams, champions, voice, compliment
from config import Config
import aiohttp
import json
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google.json"
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# Get Guild ID from right clicking on server icon
# Must have devloper mode on discord on setting>Advance>Developer Mode
#More info on tree can be found on discord.py Git Repo
@bot.command()
async def sync(ctx: Context,
               guilds: Greedy[discord.Object],
               spec: Optional[Literal["~", "*", "^"]] = None) -> None:
  if not guilds:
    if spec == "~":
      synced = await ctx.bot.tree.sync(guild=ctx.guild)
    elif spec == "*":
      ctx.bot.tree.copy_global_to(guild=ctx.guild)
      synced = await ctx.bot.tree.sync(guild=ctx.guild)
    elif spec == "^":
      ctx.bot.tree.clear_commands(guild=ctx.guild)
      await ctx.bot.tree.sync(guild=ctx.guild)
      synced = []
    else:
      synced = await ctx.bot.tree.sync()

    await ctx.send(
      f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
    )
    return

  ret = 0
  for guild in guilds:
    try:
      await ctx.bot.tree.sync(guild=guild)
    except discord.HTTPException:
      pass
    else:
      ret += 1

  await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")


@bot.event
async def on_ready():
  print(f"Logged in as {bot.user.name}")
  print("------")

  # Register cogs
  await bot.add_cog(origins.Origins(bot))
  await bot.add_cog(teams.Teams(bot))
  await bot.add_cog(champions.Champions(bot))
  await bot.add_cog(voice.Voice(bot))
  await bot.add_cog(compliment.Compliment(bot))
  print(f"Registered Cogs")
  print("------")


async def fetch_champion_image(session, champion, image_url):
  try:
    async with session.get(image_url) as response:
      if response.status != 200:
        print(
          f"Failed to fetch image for {champion} (status: {response.status})")
        return None
      return champion, image_url
  except Exception as e:
    print(f"Failed to fetch image for {champion}: {e}")
    return None


async def fetch_champion_images(session, champion_data):
  tasks = []
  for champion in champion_data['data']:
    image_url = champion_data['data'][champion]['image']['full']
    base_url = Config.IMAGE_URL
    full_url = f"{base_url}{image_url}"
    task = asyncio.create_task(
      fetch_champion_image(session, champion, full_url))
    tasks.append(task)

  results = await asyncio.gather(*tasks)
  champion_images = {key: value for key, value in results if value is not None}
  return champion_images


async def main():
  # Fetch champion data
  async with aiohttp.ClientSession() as session:
    async with session.get(Config.API_URL) as response:
      champion_data_raw = await response.json()
      champion_data = champion_data_raw['data']
  bot.champion_data = champion_data

  # Load origins data
  with open("data/origins.json", "r") as f:
    origins_data = json.load(f)
  bot.origins_data = origins_data

  # Fetch champion images
  async with aiohttp.ClientSession() as session:
    champion_images = await fetch_champion_images(session, champion_data_raw)
    bot.champion_images = champion_images

  # Run the bot
  await bot.start(Config.DISCORD_TOKEN)


if __name__ == "__main__":
  import asyncio
  asyncio.run(main())
