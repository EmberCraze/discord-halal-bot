import os
from dotenv import load_dotenv
from peewee import SqliteDatabase
from playhouse.migrate import SqliteMigrator, migrate
from halal_bot.models import QuranReadingPage


load_dotenv()
DB = os.getenv("DB_LOCATION")
db = SqliteDatabase(DB)

migrator = SqliteMigrator(db)

# migrating models
migrate(
    migrator.add_column(
        QuranReadingPage._meta.table_name,
        QuranReadingPage.time.safe_name,
        QuranReadingPage.time,
    ),
    migrator.add_column(
        QuranReadingPage._meta.table_name,
        QuranReadingPage.completions.safe_name,
        QuranReadingPage.completions,
    ),
)
