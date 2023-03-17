import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError
from bot.utils.champion_utils import get_champion_key
from typing import List
from pathlib import Path


def create_team_champion_image(champions,
                               champion_data,
                               champion_images,
                               team_name=None):
  padding = 10
  images = []
  name_texts = []

  placeholder_path = Path("data/placeholder.png")

  for champ_name in champions:
    url = champion_images.get(champ_name)

    if url is None:
      print(f"Invalid URL for champion: {champ_name}")
      print(f"URL: {url}")
      image = Image.open(placeholder_path).convert("RGBA")
    else:
      response = requests.get(url)
      image = Image.open(BytesIO(response.content)).convert("RGBA")

    images.append(image)
    name_text = champion_data[champ_name]["name"]
    name_texts.append(name_text)

  if images:
    total_width = sum(image.width
                      for image in images) + padding * (len(images) - 1)
    max_height = max(
      image.height for image in images
    ) + 50 + padding + 30  # add extra height for team name and champion names
  else:
    total_width = 0
    max_height = 0

  base_image = Image.new("RGBA", (total_width, max_height), (0, 0, 0, 0))

  font = ImageFont.truetype("data/font.ttf", 40)
  draw = ImageDraw.Draw(base_image)

  y_offset = 0
  if team_name:
    text = team_name
    text_width, text_height = draw.textsize(text, font=font)
    text_x = (base_image.width - text_width) // 2
    draw.text((text_x, y_offset), text, font=font, fill=(255, 255, 255))
    y_offset += text_height + padding

  for i, (image, name_text) in enumerate(zip(images, name_texts)):
    x_offset = i * (image.width + padding)
    base_image.paste(image, (x_offset, y_offset))
    draw = ImageDraw.Draw(base_image)
    font = ImageFont.truetype("data/font.ttf", 20)
    text = name_text
    text_width, text_height = draw.textsize(text, font=font)
    text_x = x_offset + (image.width - text_width) // 2
    text_y = y_offset + image.height + padding
    draw.text((text_x, text_y), text, font=font, fill=(255, 255, 255))

  return base_image


def create_origin_champion_image(origin_map,
                                 team_selected_champions: List[str],
                                 champion_data,
                                 champion_images,
                                 padding=10):
  images = []

  placeholder_path = Path("data/placeholder.png")

  for champ_name in team_selected_champions:
    champ_key = get_champion_key(champion_data, champ_name)
    url = champion_images.get(champ_key)

    if url is None:
      print(f"Invalid URL for champion: {champ_name}")
      print(f"URL: {url}")
      image = Image.open(placeholder_path).convert("RGBA")
    else:
      response = requests.get(url)
      try:
        image = Image.open(BytesIO(response.content)).convert("RGBA")
      except UnidentifiedImageError:
        print(f"Failed to load image for champion: {champ_name}")
        print(f"URL: {url}")
        image = Image.open(placeholder_path).convert("RGBA")

    images.append(image)

  if images:
    total_width = sum(image.width
                      for image in images) + padding * (len(images) - 1)
    max_height = max(image.height for image in images) + 70
  else:
    total_width = 0
    max_height = 0

  origin_image = Image.new("RGBA", (total_width, max_height), (0, 0, 0, 0))

  # Add origin name
  font = ImageFont.truetype("data/font.ttf", 20)
  draw = ImageDraw.Draw(origin_image)
  text = origin_map['name']
  text_width, text_height = draw.textsize(text, font=font)
  text_x = (total_width - text_width) // 2
  draw.text((text_x, 0), text, font=font, fill=(255, 255, 255))

  # Add champion images and names
  x_offset = 0
  for i, image in enumerate(images):
    champ_name = team_selected_champions[i]

    origin_image.paste(image, (x_offset, 70))
    draw = ImageDraw.Draw(origin_image)
    text = champ_name
    text_width, text_height = draw.textsize(text, font=font)
    text_x = x_offset + (image.width - text_width) // 2
    draw.text((text_x, 30), text, font=font, fill=(255, 255, 255))
    x_offset += image.width + padding

  return origin_image


def assemble_origin_images(images: List[Image.Image],
                           padding: int = 10,
                           dynamic: bool = True) -> Image:
  if not images:
    return Image.new("RGBA", (1, 1), (0, 0, 0, 0))

  # Calculate the number of rows and columns
  n_images = len(images)

  if dynamic and n_images > 1:
    n_columns = int(n_images**0.5)
    n_rows = (n_images + n_columns - 1) // n_columns
  else:
    n_columns = 1
    n_rows = n_images

  # Calculate the size of each cell
  max_width = max(img.width for img in images)
  max_height = max(img.height for img in images)
  cell_size = (max_width + padding, max_height + padding)

  # Create the final image
  final_width = n_columns * cell_size[0] - padding
  final_height = n_rows * cell_size[1] - padding
  final_image = Image.new("RGBA", (final_width, final_height), (0, 0, 0, 0))

  # Paste the images into the final image
  for i, img in enumerate(images):
    x = (i % n_columns) * cell_size[0]
    y = (i // n_columns) * cell_size[1]
    final_image.paste(img, (x, y))

  return final_image


def create_champion_image_with_name(champion_image_url: str,
                                    champion_name: str) -> Image:
  response = requests.get(champion_image_url)
  image = Image.open(BytesIO(response.content)).convert("RGBA")
  font = ImageFont.truetype("data/font.ttf", 18)
  text_color = (255, 255, 255)

  draw = ImageDraw.Draw(image)
  text_width, text_height = draw.textsize(champion_name, font=font)

  # Calculate the position to place the champion name
  x = (image.width - text_width) / 2
  y = image.height + 10

  # Create a new image with the required height to display the champion name
  new_image = Image.new("RGBA", (image.width, image.height + text_height + 10),
                        (0, 0, 0, 0))

  # Paste the champion image onto the new image
  new_image.paste(image, (0, 0))

  # Draw the champion name below the image
  draw = ImageDraw.Draw(new_image)
  draw.text((x, y), champion_name, fill=text_color, font=font)

  return new_image
