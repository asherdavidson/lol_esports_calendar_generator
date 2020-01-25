from datetime import timedelta
from functools import lru_cache
from typing import List, Optional, Iterable

import redis
from dateutil.parser import parse
from icalendar import Event, Calendar
from peewee import *

from app_config import DB_FILE_NAME

sqlite_db = SqliteDatabase(DB_FILE_NAME)
redis_db = redis.Redis(host='localhost', port=6379, db=0)


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

    @staticmethod
    @lru_cache  # cache the items once per day (i.e. clear the cache once per day)
    def get_front_page_items(date) -> Iterable['League']:
        return list(League.select().order_by(League.priority))

    @staticmethod
    def query_league_matches(leagues):
        return (Match
                .select(Match, League)
                .join(League)
                .where(League.slug.in_(leagues))
                .order_by(Match.start_time))

    @staticmethod
    def generate_cal(leagues) -> bytes:
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


class CalendarCache:
    @staticmethod
    def clear():
        redis_db.delete(*redis_db.keys())

    @staticmethod
    def get_calender(leagues: List[str]) -> bytes:
        id = 'calendar-cache:' + ','.join(sorted(leagues))

        calendar: Optional[bytes] = redis_db.get(id)

        if calendar is not None:
            return calendar

        calendar = League.generate_cal(leagues)
        redis_db.set(id, calendar)

        return calendar


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


if __name__ == '__main__':
    # drop_tables()
    # create_tables()

    CalendarCache.clear()
