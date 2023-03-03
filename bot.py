import datetime
import os
import requests
import random
from typing import Literal, Union, NamedTuple
from enum import Enum

from table2ascii import table2ascii as t2a

import discord
from discord import app_commands
from dotenv import load_dotenv

from halal_bot.client import MyClient
from halal_bot.models import db, User, QuranReadingPage


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
DB = os.getenv("DB_LOCATION")

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
        .order_by(
            -QuranReadingPage.completions,
            -QuranReadingPage.time,
            -QuranReadingPage.page,
        )
        .execute()
    )

    header = ["Rank", "Name", "Page", "Time", "Completions"]
    body = []
    for index, entry in enumerate(entries):
        member = interaction.guild.get_member(entry.user.user_id)
        member_info = member.nick if member.nick else member.name

        body.append([index + 1, member_info, entry.page, entry.time, entry.completions])

    db.close()
    table = t2a(header=header, body=body, first_col_heading=True)
    await interaction.response.send_message(f"```\n{table}\n```")
    # await interaction.response.send_message(embed=embed)


@client.tree.command(name="update-reading-progress")
@app_commands.describe(
    page="Pages of the Quran to increment",
    time="Time spent reading to increment",
    completions="Completions of the Quran to increment",
)
async def update_reading_progress(
    interaction: discord.Interaction,
    # This makes it so the page parameter can only be between 0 to 604.
    page: Union[app_commands.Range[int, -999, 999], None],
    time: Union[app_commands.Range[int, -999, 999], None],
    completions: Union[app_commands.Range[int, -999, 999], None],
):
    """Sets your progress in quran reading"""
    page = page if page else 0
    time = time if time else 0
    completions = completions if completions else 0

    db.connect()

    user, _ = User.get_or_create(
        user_id=interaction.user.id, guild_id=interaction.guild.id
    )
    new_time = datetime.timedelta(minutes=time)
    defaults = {"time": new_time, "page": page, "completions": completions}

    quran_reading_page, created = QuranReadingPage.get_or_create(
        user=user.id, defaults=defaults
    )

    if not created:
        page = page + quran_reading_page.page
        new_time = new_time + quran_reading_page.time
        completions = completions + quran_reading_page.completions
        QuranReadingPage.replace(
            user=user.id,
            page=page,
            time=new_time,
            completions=completions,
        ).execute()

    db.close()

    message = (
        f"Your progres is Page({page}) Time({new_time}) Completions({completions})"
    )

    await interaction.response.send_message(message)


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
