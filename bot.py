import os
import random
import discord
from discord.ext import commands
import requests

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

CHANNEL_ID = 701417126392627341
RIOT_API_KEY = os.getenv("RIOT_API_KEY")


def get_champions_by_origin(origin: str):
  champion_data_url = "https://ddragon.leagueoflegends.com/cdn/11.18.1/data/en_US/champion.json"
  response = requests.get(champion_data_url).json()
  champion_data = response['data']

  champions = [{
    "name": champ_data["name"],
    "title": champ_data["title"],
    "id": champ_id,
  } for champ_id, champ_data in champion_data.items()
               if champ_data["blurb"].lower().count(origin.lower()) > 0]

  return champions


@bot.event
async def on_ready():
  print(f"Logged in as {bot.user.name}")
  print("------")


@bot.command(name="team")
async def team(ctx):
  origin = ctx.message.content.split(" ")[1]
  print(f"Received team command with origin={origin}")

  champions = get_champions_by_origin(origin)
  print(champions)

  if len(champions) == 0:
    response = f"No champions found with the origin '{origin}'. Please check the origin and try again."
  elif len(champions) < 5:
    response = f"Not enough champions found for {origin}."
  else:
    selected_champions = random.sample(champions, 5)
    response = f"Here is your {origin} team:\n"
    for champ_data in selected_champions:
      response += f"{champ_data['name']} - {champ_data['title']}\n"

  await ctx.send(response)


bot.run(os.getenv("DISCORD_TOKEN"))
