import json


def get_champions_by_origin(origins_data, origin):
  champions = []
  for origin_entry in origins_data:
    if origin_entry.lower() == origin.lower():
      champions = origins_data[origin_entry]
      break
  return champions


def get_champion_key(champion_data, champion_name):
  for key, data in champion_data.items():
    if data["name"] == champion_name:
      return key
  return None
