import openai
import discord
from discord.ext import commands
from discord import app_commands
from config import Config
import random
from google.cloud import texttospeech
import io
import tempfile
import os
from google.oauth2 import service_account

openai.api_key = Config.OPENAI_TOKEN

# Initialize the Google Text-to-Speech client
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file("google.json")
tts_client = texttospeech.TextToSpeechClient(credentials=credentials)

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

            # Use the Google Text-to-Speech library to generate an audio clip of the message being spoken
            synthesis_input = texttospeech.SynthesisInput(text=compliment)
            voice = texttospeech.VoiceSelectionParams(language_code="pl-PL", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE)
            audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

            response = tts_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

            # Save the audio to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as audio_file:
                audio_file.write(response.audio_content)
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

            await interaction.followup.send(f"Komplement wysłany do {selected_member.display_name}!")

        except Exception as e:
            print(f"An error occurred while processing the command: {str(e)}")
            raise e

