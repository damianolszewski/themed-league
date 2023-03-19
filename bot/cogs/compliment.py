import openai
import discord
from discord.ext import commands
from discord import app_commands
from config import Config
import random
import pyttsx3
import tempfile
import os

openai.api_key = Config.OPENAI_TOKEN

class Compliment(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="compliment",
        description="Wyślij komplement losowej osobie na twoim kanale głosowym."
    )
    async def compliment(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer()

            if not interaction.user.voice:
                await interaction.followup.send(
                    "Musisz być na kanale głosowym żeby użyć tej komendy!"
                )
                return

            channel = interaction.user.voice.channel
            members = channel.members

            if not members:
                await interaction.followup.send("Nie ma nikogo na twoim kanale głosowym!")
                return

            selected_member = random.choice(members)

            # Use OpenAI's GPT-3 API to generate a positive message to send to the selected member
            prompt = f"Powiedz komplement o {selected_member.display_name} w języku polskim. Pamiętaj żeby w zdaniu użyć imienia osoby do której się zwracasz (czyli {selected_member.display_name})"
            response = openai.Completion.create(
                engine="text-davinci-002",
                prompt=prompt,
                max_tokens=60,
                n=1,
                stop=None,
                temperature=0.5,
            )

            compliment = response.choices[0].text.strip()

            # Use the pyttsx3 library to generate an audio clip of the message being spoken
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)  # Speed of speech
            engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)
            engine.save_to_file(compliment, 'output.mp3')
            engine.runAndWait()

            # Send the audio clip to the selected member in the voice channel
            voice_client = await channel.connect()
            audio_source = discord.FFmpegPCMAudio('output.mp3')
            voice_client.play(audio_source)
            while voice_client.is_playing():
                pass
            await voice_client.disconnect()

            # Remove the temporary audio file
            os.unlink('output.mp3')

            await interaction.followup.send(f"Komplement wysłany do {selected_member.display_name}!")

        except Exception as e:
            print(f"An error occurred while processing the command: {str(e)}")
            raise e
