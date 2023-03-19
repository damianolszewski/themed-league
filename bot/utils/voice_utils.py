import discord
from config import Config
import random
from google.cloud import texttospeech
import io
import tempfile
import os
from google.oauth2 import service_account
from gtts import gTTS
import shutil
from discord.opus import Encoder
import openai
from enum import Enum

# ...

class InteractionType(Enum):
    COMPLIMENT = 1
    JOKE = 2

openai.api_key = Config.OPENAI_TOKEN

credentials = service_account.Credentials.from_service_account_file("google.json")
tts_client = texttospeech.TextToSpeechClient(credentials=credentials)

polish_wavenet_voices = [
    "pl-PL-Wavenet-A",
    "pl-PL-Wavenet-B",
    "pl-PL-Wavenet-C",
    "pl-PL-Wavenet-D",
    "pl-PL-Wavenet-E",
]

def get_voice_channel_members(interaction: discord.Interaction) -> list[discord.Member]:
    """Returns a list of members in the voice channel the user is currently in."""
    if not interaction.user.voice:
        return []

    voice_channel = interaction.user.voice.channel
    return [member for member in voice_channel.members if not member.bot]

async def voiceInteraction(interaction_type: InteractionType, interaction: discord.Interaction):
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

        compliment = f"Powiedz komplement o {selected_member.display_name} w języku polskim. Pamiętaj żeby w zdaniu użyć imienia osoby do której się zwracasz (czyli {selected_member.display_name}). Postaraj się żeby komplement był kreatywny. Czasami komplement może być dłuższy (nie zawsze musi być). Postaraj się zapmiętać ten komplement aby w późniejszy komplementach móc odnieść się do poprzednich. Czasami możesz odnosić się do poprzednich komplementów tworząc nowe komplementy."
        joke = f"Powiedz żart o {selected_member.display_name} w języku polskim. Przykładowe żarty: 'Przynosisz wszystkim tyle radości, kiedy wychodzisz z pokoju' 'Jesteś ludzkim odpowiednikiem nagrody za uczestnictwo', ' Każdy ma w życiu jakiś cel, twoim jest zostać dawcą organów', 'Od chwili, gdy zobaczyłem cię po raz pierwszy, wiedziałem, że chcę spędzić resztę życia unikając cię, 'Jesteś bardziej rozczarowujący niż niesolony precel', 'Możesz przywitać się z moim środkowym palcem', Pamiętaj żeby nie używać tych przykładowych żartów (bardzo ważne!) -postaraj się częściej tworzyć swoje , Pamiętaj żeby w zdaniu użyć imienia osoby do której się zwracasz (czyli {selected_member.display_name}). Postaraj się żeby żart był kreatywny. Czasami żart może być dłuższy (nie zawsze musi być). Postaraj się zapmiętać ten żart aby w późniejszy żart móc odnieść się do poprzednich. Czasami możesz odnosić się do poprzednich żartów tworząc nowe żarty."

        if interaction_type == InteractionType.COMPLIMENT:
            prompt = compliment
        elif interaction_type == InteractionType.JOKE:
            prompt = joke
        else:
            raise ValueError("Invalid interaction type")

        # Use OpenAI's GPT-3 API to generate a positive message to send to the selected member
        
        response = openai.Completion.create(
            engine="gpt-3.5-turbo",
            prompt=prompt,
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.5,
        )

        print(f"Response: {response}")

        compliment = response.choices[0].text.strip()

        selected_voice = random.choice(polish_wavenet_voices)

        try:
            print("Using google tts")
            # Use the Google Text-to-Speech library to generate an audio clip of the message being spoken
            synthesis_input = texttospeech.SynthesisInput(text=compliment)
            voice = texttospeech.VoiceSelectionParams(
                language_code="pl-PL", 
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
                name=selected_voice
            )
            audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

            response = tts_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

            # Save the audio to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as audio_file:
                audio_file.write(response.audio_content)
                audio_file.flush()

        except Exception as e:
            print(f"Using gTTS as a fallback: {str(e)}")
            # Use gTTS as a fallback
            tts = gTTS(compliment, lang="pl")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as audio_file:
                tts.save(audio_file.name)
                audio_file.flush()

        # Send the audio clip to the selected member in the voice channel
        voice_client = await channel.connect()
        audio_source = discord.FFmpegOpusAudio(audio_file.name, options="-b:a 64k", bitrate=64)
        voice_client.play(audio_source)
        while voice_client.is_playing():
            pass
        await voice_client.disconnect()

        # Remove the temporary audio file
        os.unlink(audio_file.name)

        await interaction.followup.send(f"Mam coś do powiedzenia o {selected_member.display_name}!")
    except Exception as e:
        print(f"An error occurred while processing the command: {str(e)}")
        raise e