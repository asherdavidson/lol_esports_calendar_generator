import os
from datetime import timedelta, date
from functools import lru_cache
from typing import Tuple, Optional

from dateutil.parser import parse
from icalendar import Event, Calendar
from sqlalchemy import create_engine, String, Integer, DateTime, ForeignKey, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker, joinedload


def get_database_url() -> str:
    """Get database URL from DATABASE_URL environment variable.

    Raises ValueError if DATABASE_URL is not set.
    """
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        raise ValueError("DATABASE_URL environment variable is required")

    # Handle postgres:// vs postgresql:// (some providers use postgres://)
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    return database_url


def create_db_engine():
    """Create SQLAlchemy engine with PostgreSQL settings."""
    database_url = get_database_url()

    # Check if we need SSL (production typically requires it)
    connect_args = {}
    if os.environ.get("FLASK_ENV") == "production":
        connect_args["sslmode"] = "require"

    return create_engine(
        database_url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        connect_args=connect_args,
    )


engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class League(Base):
    __tablename__ = "league"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    slug: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    region: Mapped[str] = mapped_column(String, nullable=False)
    image_url: Mapped[str] = mapped_column(String, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False)

    matches: Mapped[list["Match"]] = relationship("Match", back_populates="league")

    def __str__(self) -> str:
        return self.name

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "slug": self.slug,
            "name": self.name,
        }

    @staticmethod
    @lru_cache
    def get_front_page_items(date: date) -> list["League"]:
        """Get all leagues ordered by priority. Cached once per day."""
        session = SessionLocal()
        try:
            stmt = select(League).order_by(League.priority)
            return list(session.scalars(stmt))
        finally:
            session.close()

    @staticmethod
    def query_league_matches(leagues: Tuple[str, ...]) -> list["Match"]:
        """Get matches for given league slugs, ordered by start time."""
        session = SessionLocal()
        try:
            stmt = (
                select(Match)
                .options(joinedload(Match.league))
                .join(League)
                .where(League.slug.in_(leagues))
                .order_by(Match.start_time)
            )
            return list(session.scalars(stmt).unique())
        finally:
            session.close()

    @staticmethod
    @lru_cache
    def generate_cal(leagues: Tuple[str, ...], date: date) -> bytes:
        """Generate iCal calendar for given league slugs. Cached once per day."""
        matches = League.query_league_matches(leagues)

        cal = Calendar()
        cal.add("summary", "LoL eSports Calendar")
        cal.add("prodid", "-//LoL eSports Calendar Generator//asherdavidson.net//")
        cal.add("x-wr-calname", "LoL eSports Calendar")

        for match in matches:
            cal.add_component(match.get_ical_event_with_time())

        return cal.to_ical()


class Match(Base):
    __tablename__ = "match"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    start_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    block_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    number_of_matches: Mapped[int] = mapped_column(Integer, nullable=False)
    team_a: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    team_b: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    league_id: Mapped[str] = mapped_column(ForeignKey("league.id"), nullable=False)
    league: Mapped["League"] = relationship("League", back_populates="matches")

    def __str__(self) -> str:
        block_name_formatted = f" {self.block_name}" if self.block_name else ""
        return f"{self.league.name}{block_name_formatted}: {self.team_a} vs {self.team_b} (bo{self.number_of_matches})"

    def get_ical_event_with_time(self) -> Event:
        dtstart = self.start_time if hasattr(self.start_time, 'date') else parse(str(self.start_time))
        dtend = dtstart + timedelta(hours=self.number_of_matches)
        dtstamp = dtstart.date()

        event = Event()
        event.add("summary", str(self))
        event.add("dtstart", dtstart)
        event.add("dtend", dtend)
        event.add("dtstamp", dtstamp)

        return event


MODELS = [League, Match]


def run_migrations():
    """Run Alembic migrations to head."""
    from alembic.config import Config
    from alembic import command

    # Get the directory where alembic.ini is located
    base_dir = os.path.dirname(os.path.dirname(__file__))
    alembic_cfg = Config(os.path.join(base_dir, "alembic.ini"))

    # Set the database URL from environment
    alembic_cfg.set_main_option("sqlalchemy.url", get_database_url())

    print("Running database migrations...")
    command.upgrade(alembic_cfg, "head")
    print("Migrations completed successfully!")


def create_tables():
    """Create all tables (for development/testing only)."""
    print(f"WARNING: Creating tables: {', '.join(m.__tablename__ for m in MODELS)}")
    Base.metadata.create_all(engine)


def drop_tables():
    """Drop all tables (for development/testing only)."""
    print(f"WARNING: Dropping tables: {', '.join(m.__tablename__ for m in MODELS)}")
    Base.metadata.drop_all(engine)
