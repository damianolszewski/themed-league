import openai
import discord
from discord.ext import commands
from discord.app import commands as app_commands
from config import Config
import random
from gtts import gTTS
import io
import tempfile
import os

openai.api_key = Config.OPENAI_TOKEN

class Compliment(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="compliment",
        description="Sends a positive message to a random member of your voice channel."
    )
    async def compliment(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer()

            if not interaction.user.voice:
                await interaction.followup.send(
                    "You must be in a voice channel to use this command!"
                )
                return

            channel = interaction.user.voice.channel
            members = channel.members

            if not members:
                await interaction.followup.send("No members found in the voice channel!")
                return

            selected_member = random.choice(members)

            # Use OpenAI's GPT-3 API to generate a positive message to send to the selected member
            prompt = f"Compliment {selected_member.display_name} in Polish"
            response = openai.Completion.create(
                engine="text-davinci-002",
                prompt=prompt,
                max_tokens=60,
                n=1,
                stop=None,
                temperature=0.5,
            )

            compliment = response.choices[0].text.strip()

            # Use the gTTS library to generate an audio clip of the message being spoken
            tts = gTTS(text=compliment, lang="pl")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as audio_file:
                tts.save(audio_file.name)
                audio_file.flush()

                # Send the audio clip to the selected member in the voice channel
                voice_client = await channel.connect()
                audio_source = discord.FFmpegPCMAudio(audio_file.name)
                voice_client.play(audio_source)
                while voice_client.is_playing():
                    pass
                await voice_client.disconnect()

            # Remove the temporary audio file
            os.unlink(audio_file.name)

            await interaction.followup.send(f"Sent a positive message to {selected_member.display_name}!")

        except Exception as e:
            print(f"An error occurred while processing the command: {str(e)}")
            raise e
