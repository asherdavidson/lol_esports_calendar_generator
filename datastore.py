from datetime import timedelta
from typing import List, Optional, Iterable

from dateutil.parser import parse
from icalendar import Event, Calendar
from peewee import *

from app_config import DB_FILE_NAME

db = SqliteDatabase(DB_FILE_NAME)


class BaseModel(Model):
    class Meta:
        database = db


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
    def get_front_page_items() -> Iterable['League']:
        return League.select().order_by(League.priority)

    @staticmethod
    def query_league_matches(leagues):
        return (Match
                .select(Match, League)
                .join(League)
                .where(League.slug.in_(leagues))
                .order_by(Match.start_time))

    @staticmethod
    def generate_cal(leagues) -> Calendar:
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
        start_time = parse(self.start_time)

        delta = timedelta(hours=self.number_of_matches)

        dtstart = start_time
        dtend = start_time + delta
        dtstamp = start_time.date()

        event = Event()
        event.add('summary', str(self))
        event.add('dtstart', dtstart)
        event.add('dtend', dtend)
        event.add('dtstamp', dtstamp)

        return event


class CalendarCache(BaseModel):
    id = CharField(primary_key=True)
    calendar = BlobField()

    @staticmethod
    def clear_cache():
        print('WARNING: Clearing the calendar cache')
        CalendarCache.delete()  # deletes all rows from table

    @staticmethod
    def get_or_create_calendar(leagues: List[str]) -> bytes:
        id = ','.join(sorted(leagues))

        model: Optional[CalendarCache] = CalendarCache.get_or_none(id=id)

        if model is not None:
            return model.calendar

        calendar = League.generate_cal(leagues)
        CalendarCache.create(id=id, calendar=calendar)
        return calendar


MODELS = [
    League,
    Match,
    CalendarCache,
]


def create_tables():
    print(f'WARNING: Creating tables: {", ".join(map(str, MODELS))}')
    db.create_tables(MODELS)


def drop_tables():
    print(f'WARNING: Dropping tables: {", ".join(map(str, MODELS))}')
    db.drop_tables(MODELS)


if __name__ == '__main__':
    # drop_tables()
    # create_tables()

    CalendarCache.clear_cache()
