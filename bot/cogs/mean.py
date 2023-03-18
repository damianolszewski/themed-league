import openai
import discord
from discord.ext import commands
from discord import app_commands
from config import Config
import random

openai.api_key = Config.OPENAI_KEY

class Mean(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="mean",
        description="Sends a mean message to a random member of your voice channel."
    )
    async def mean(self, interaction: discord.Interaction):
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

            # Use a text-to-speech service to generate an audio clip of the message being spoken
            # This is an example using Google's Text-to-Speech API, but there are many others available
            from google.cloud import texttospeech
            import io

            client = texttospeech.TextToSpeechClient()
            synthesis_input = texttospeech.SynthesisInput(text=compliment)
            voice = texttospeech.VoiceSelectionParams(
                language_code="pl-PL",
                ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )

            response = client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )

            audio_bytes = response.audio_content

            # Send the audio clip to the selected member in the voice channel
            voice_client = await channel.connect()
            audio_source = discord.FFmpegPCMAudio(io.BytesIO(audio_bytes))
            voice_client.play(audio_source)
            await interaction.followup.send(f"Sent a positive message to {selected_member.display_name}!")
            
        except Exception as e:
            print(f"An error occurred while processing the command: {str(e)}")
            raise e