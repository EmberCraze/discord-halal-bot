import discord
from discord import app_commands
from models import db, User, QuranReadingPage


DEV_GUILD = discord.Object(id=552551959144562719)
PROD_GUILD = discord.Object(id=983151312189403216)

intents = discord.Intents.default()
intents.members = True


class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        sync = False
        if sync:
            self.tree.copy_global_to(guild=DEV_GUILD)
            await self.tree.sync(guild=DEV_GUILD)

            self.tree.copy_global_to(guild=PROD_GUILD)
            await self.tree.sync(guild=PROD_GUILD)

        # Setup the database if nothing is present
        db.connect()
        db.create_tables([User, QuranReadingPage])
        db.close()
