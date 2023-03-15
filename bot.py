import os
import random
import csv
import discord

from discord.ext import commands

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

CHANNEL_ID = 701417126392627341

champion_roles = {}

# Read champion data from stats.csv file to determine their roles
with open('stats.csv', newline='') as csvfile:
  reader = csv.reader(csvfile, delimiter=',', quotechar='"')
  next(reader)  # skip header row
  for row in reader:
    champion_name = row[0]
    champion_roles[champion_name] = []
    for i in range(1, len(row)):
      if row[i] != '':
        champion_roles[champion_name].append(row[i])


def get_champions_by_role(role):
  champions = []
  for champion_name in champion_roles:
    if role in champion_roles[champion_name]:
      champions.append(champion_name)
  return champions


def get_champion_role(champions, role):
  print(f"get {role}")
  role_champions = []
  for champ in champions:
    role_champions.append(champ)
  return random.choice(
    role_champions) if role_champions else "No available champion"


@bot.event
async def on_ready():
  print(f"Logged in as {bot.user.name}")
  print("------")


@bot.command(name="team")
async def team(ctx):
  origin = ctx.message.content.split(" ")[1]
  print(f"Received team command with origin={origin}")
  roles = ["Top", "Jungle", "Middle", "ADC", "Support"]
  champions_by_role = {}
  for role in roles:
    champions = get_champions_by_role(role)
    print(f"Found {len(champions)} champions for role={role}")
    champions_by_role[role] = champions
  team = {
    "Top": get_champion_role(champions_by_role["Top"], "Top"),
    "Jungle": get_champion_role(champions_by_role["Jungle"], "Jungle"),
    "Middle": get_champion_role(champions_by_role["Middle"], "Middle"),
    "ADC": get_champion_role(champions_by_role["ADC"], "ADC"),
    "Support": get_champion_role(champions_by_role["Support"], "Support"),
  }
  response = f"Here is your {origin} team:\n\n"
  for role, champion in team.items():
    response += f"{role}: {champion}\n"
  print(f"Sending response: {response}")
  await ctx.send(response)


bot.run(os.getenv("DISCORD_TOKEN"))
