import os
import random
import requests

from discord.ext import commands


bot = commands.Bot(command_prefix='!')

def get_champions_by_origin(origin):
    url = f'https://api.champions.gg/v2/champions?elo=GOLD&champData=roles&limit=200'
    response = requests.get(url)
    champions_data = response.json()['data']
    champions = []
    for champ in champions_data:
        if origin in champ['attributes']['tags']:
            champions.append(champ)
    return champions

def get_champion_role(champions, role):
    role_champions = []
    for champ in champions:
        if role in champ['attributes']['roles']:
            role_champions.append(champ['attributes']['name'])
    return random.choice(role_champions) if role_champions else 'No available champion'

@bot.command()
async def team(ctx, origin: str):
    champions = get_champions_by_origin(origin)
    team = {
        'Top': get_champion_role(champions, 'Top'),
        'Jungle': get_champion_role(champions, 'Jungle'),
        'Middle': get_champion_role(champions, 'Middle'),
        'ADC': get_champion_role(champions, 'ADC'),
        'Support': get_champion_role(champions, 'Support')
    }
    response = f"Here is your {origin} team:\n\n"
    for role, champion in team.items():
        response += f"{role}: {champion}\n"
    await ctx.send(response)

bot.run(os.environ['DISCORD_TOKEN'])