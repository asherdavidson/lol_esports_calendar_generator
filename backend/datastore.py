from datetime import timedelta, date
from functools import lru_cache
from typing import Iterable, Tuple

from dateutil.parser import parse
from icalendar import Event, Calendar
from peewee import SqliteDatabase, Model, CharField, IntegerField, DateTimeField, ForeignKeyField

from app_config import DB_FILE_NAME

sqlite_db = SqliteDatabase(DB_FILE_NAME)


class BaseModel(Model):
    class Meta:
        database = sqlite_db


class League(BaseModel):
    id = CharField(primary_key=True)
    slug = CharField()
    name = CharField()
    region = CharField()
    image_url = CharField()
    priority = IntegerField()

    # matches

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            'id': self.id,
            'slug': self.slug,
            'name': self.name,
        }

    @staticmethod
    @lru_cache  # cache the items once per day (i.e. clear the cache once per day)
    def get_front_page_items(date: date) -> Iterable['League']:
        return list(League.select().order_by(League.priority))

    @staticmethod
    def query_league_matches(leagues):
        return (Match
                .select(Match, League)
                .join(League)
                .where(League.slug.in_(leagues))
                .order_by(Match.start_time))

    @staticmethod
    @lru_cache  # cache the items once per day (i.e. clear the cache once per day)
    def generate_cal(leagues: Tuple[str], date: date) -> bytes:
        matches = League.query_league_matches(leagues)

        cal = Calendar()
        cal.add('summary', "LoL eSports Calendar")
        cal.add('prodid', '-//LoL eSports Calendar Generator//asherdavidson.net//')
        cal.add('x-wr-calname', "LoL eSports Calendar")

        for match in matches:
            cal.add_component(match.get_ical_event_with_time())

        return cal.to_ical()


class Match(BaseModel):
    id = CharField(primary_key=True)
    start_time = DateTimeField()
    block_name = CharField(null=True)
    number_of_matches = IntegerField()
    team_a = CharField(null=True)
    team_b = CharField(null=True)

    league = ForeignKeyField(League, backref='matches')

    def __str__(self):
        block_name_formatted = f' {self.block_name}' if self.block_name else ''
        return f'{self.league.name}{block_name_formatted}: {self.team_a} vs {self.team_b} (bo{self.number_of_matches})'

    def get_ical_event_with_time(self):
        dtstart = parse(self.start_time)
        dtend = dtstart + timedelta(hours=self.number_of_matches)
        dtstamp = dtstart.date()

        event = Event()
        event.add('summary', str(self))
        event.add('dtstart', dtstart)
        event.add('dtend', dtend)
        event.add('dtstamp', dtstamp)

        return event


MODELS = [
    League,
    Match,
]


def create_tables():
    print(f'WARNING: Creating tables: {", ".join(map(str, MODELS))}')
    sqlite_db.create_tables(MODELS)


def drop_tables():
    print(f'WARNING: Dropping tables: {", ".join(map(str, MODELS))}')
    sqlite_db.drop_tables(MODELS)

# if __name__ == '__main__':
#     drop_tables()
#     create_tables()
