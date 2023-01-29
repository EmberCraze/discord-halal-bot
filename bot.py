import os
from typing import Literal, Union, NamedTuple
from enum import Enum

import discord
from discord import app_commands
from dotenv import load_dotenv

from client import MyClient
from models import db, User, QuranReadingPage


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

client = MyClient()


@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    print("------")
    for guild in client.guilds:
        print(guild.name, guild.id)


@client.tree.command(name="quran-leaderboard")
async def quran_leaderboard(interaction: discord.Interaction):
    """Dispay quran reading leaderboard"""

    embed = discord.Embed(title="Quran Leaderboard")
    db.connect()
    entries = (
        QuranReadingPage.select()
        .join(User)
        .where(User.guild_id == interaction.guild.id)
        .execute()
    )

    for index, entry in enumerate(entries):
        member = interaction.guild.get_member(entry.user.user_id)
        member_info = member.nick if member.nick else member.name
        if index == 0:
            embed.add_field(
                name="Name",
                value=member_info,
                inline=True,
            )
            embed.add_field(name="Page", value=entry.page)
        else:
            embed.insert_field_at(
                index=index,
                name="",
                value=member_info,
                inline=True,
            )
            embed.insert_field_at(index=index, name="", value=entry.page, inline=True)

    db.close()
    await interaction.response.send_message(embed=embed)


@client.tree.command()
@app_commands.describe(page="The page were you are it in your reading")
async def update_reading_progress(
    interaction: discord.Interaction,
    # This makes it so the first parameter can only be between 0 to 100.
    page: app_commands.Range[int, 0, 604],
):
    """Sets your progress in quran reading"""

    db.connect()

    user, _ = User.get_or_create(
        user_id=interaction.user.id, guild_id=interaction.guild.id
    )
    QuranReadingPage.replace(user=user.id, page=page).execute()

    db.close()

    await interaction.response.send_message(
        f"Your page progress is now set to {page}", ephemeral=True
    )


client.run(TOKEN)
