import os
import requests
import random
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
        .order_by(-QuranReadingPage.page)
        .execute()
    )

    for index, entry in enumerate(entries):
        member = interaction.guild.get_member(entry.user.user_id)
        member_info = member.nick if member.nick else member.name
        if index == 0:
            embed.add_field(name="Name", value=member_info, inline=True)
            embed.add_field(name="Page", value=entry.page)
        else:
            embed.add_field(name="", value=member_info, inline=True)
            embed.add_field(name="", value=entry.page, inline=True)

        # Add spacer
        embed.add_field(name="", value="", inline=False)

    db.close()
    await interaction.response.send_message(embed=embed)


@client.tree.command(name="update-reading-progress")
@app_commands.describe(page="The lastest page you have completed reading")
async def update_reading_progress(
    interaction: discord.Interaction,
    # This makes it so the page parameter can only be between 0 to 604.
    page: app_commands.Range[int, 0, 604],
):
    """Sets your progress in quran reading"""

    db.connect()

    user, _ = User.get_or_create(
        user_id=interaction.user.id, guild_id=interaction.guild.id
    )
    QuranReadingPage.replace(user=user.id, page=page).execute()

    db.close()

    await interaction.response.send_message(f"Your page progress is now set to {page}")


@client.tree.command(name="a-random-name-of-allah")
async def random_name_of_allah(interaction: discord.Interaction):
    """Get a random name of Allah (SWT)"""

    random_number = random.randint(1, 99)

    # Make a GET request to the API endpoint
    response = requests.get(f"https://api.aladhan.com/v1/asmaAlHusna/{random_number}")

    name = ""
    transliteration = ""
    meaning = ""

    # Check the status code of the response to make sure the request was successful
    if response.status_code == 200:
        # Get the JSON data from the response
        response = response.json()
        data = response.get("data")[0]

        name = data.get("name")
        transliteration = data.get("transliteration")
        meaning = data.get("en").get("meaning")
    else:
        await interaction.response.send_message("Something went wront!")
        return

    embed = discord.Embed()

    embed.add_field(name="Name", value=name, inline=True)
    embed.add_field(name="Transliteration", value=transliteration, inline=True)
    embed.add_field(name="Meaning", value=meaning, inline=True)

    # Add spacer
    embed.add_field(name="", value="", inline=False)

    await interaction.response.send_message(embed=embed)


client.run(TOKEN)
