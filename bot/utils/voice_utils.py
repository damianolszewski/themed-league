import discord

def get_voice_channel_members(interaction: discord.Interaction) -> list[discord.Member]:
    """Returns a list of members in the voice channel the user is currently in."""
    if not interaction.user.voice:
        return []

    voice_channel = interaction.user.voice.channel
    return [member for member in voice_channel.members if not member.bot]