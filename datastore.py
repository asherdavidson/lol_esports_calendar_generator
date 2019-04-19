from datetime import timedelta, timezone

from dateutil.parser import parse
from icalendar import Event
from peewee import *


def utc_to_local(utc_dt, tz):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=tz)


DB_FILE_NAME = 'datastore.db'

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
    def get_front_page_items():
        return League.select().order_by(League.priority)


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
        # dtstart = utc_to_local(self.scheduled_time, tz)
        # dtend = utc_to_local(self.scheduled_time + delta, tz)
        # dtstamp = utc_to_local(self.scheduled_time, tz).date()

        dtstart = start_time
        dtend = start_time + delta
        dtstamp = start_time.date()

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
    db.create_tables(MODELS)


def drop_tables():
    db.drop_tables(MODELS)


if __name__ == '__main__':
    drop_tables()
    create_tables()
