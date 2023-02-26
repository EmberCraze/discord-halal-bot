import os
from dotenv import load_dotenv
from peewee import (
    SqliteDatabase,
    Model,
    IntegerField,
    ForeignKeyField,
    Check,
)

from halal_bot.core.fields import TimedeltaField


load_dotenv()
DB = os.getenv("DB_LOCATION")
db = SqliteDatabase(DB)


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    user_id = IntegerField()
    guild_id = IntegerField()

    class Meta:
        indexes = ((("user_id", "guild_id"), True),)


class QuranReadingPage(BaseModel):
    user = ForeignKeyField(User, unique=True)
    page = IntegerField(constraints=[Check("page < 605")])
    time = TimedeltaField(default=0)
    completions = IntegerField(default=0)
