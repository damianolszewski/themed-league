import os


class Config:
  PATCH_VERSION = "13.5.1"
  DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
  RIOT_API_KEY = os.getenv("RIOT_API_KEY")
  API_URL = f"https://ddragon.leagueoflegends.com/cdn/{PATCH_VERSION}/data/en_US/champion.json"
  IMAGE_URL = f"http://ddragon.leagueoflegends.com/cdn/{PATCH_VERSION}/img/champion/"