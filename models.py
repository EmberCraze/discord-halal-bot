from peewee import (
    SqliteDatabase,
    Model,
    IntegerField,
    ForeignKeyField,
    Check,
)


db = SqliteDatabase("halal.db")


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
