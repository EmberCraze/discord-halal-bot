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
    id = IntegerField(primary_key=True)
    guild_id = IntegerField()


class QuranReadingPage(BaseModel):
    user = ForeignKeyField(User)
    page = IntegerField(constraints=[Check("page < 604")])
