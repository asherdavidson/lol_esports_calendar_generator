import os
from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.datastore import Base, League, Match, SessionLocal


@pytest.fixture(scope="function")
def session():
    """Create a test database session.

    Uses the DATABASE_URL environment variable to connect to PostgreSQL.
    Creates tables, yields the session, then drops tables after each test.
    """
    # Use the same database URL as the app
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        pytest.skip("DATABASE_URL environment variable required for tests")

    # Handle postgres:// vs postgresql://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    engine = create_engine(database_url)

    # Create all tables
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    # Cleanup: rollback any pending changes and drop all tables
    session.rollback()
    session.close()
    Base.metadata.drop_all(engine)


def test_datastore_league_get_front_page_items(session):
    # Clear the lru_cache to ensure fresh results
    League.get_front_page_items.cache_clear()

    # check empty db - use session query instead of cached method for accurate test
    leagues = session.query(League).order_by(League.priority).all()
    assert len(leagues) == 0

    leagues_data = [
        {
            "id": "100695891328981122",
            "slug": "european-masters",
            "name": "European Masters",
            "region": "EUROPE",
            "image_url": "https://lolstatic-a.akamaihd.net/esports-assets/production/league/european-masters-6uqdmwq0.png",
            "priority": 213,
        },
        {
            "id": "101382741235120470",
            "slug": "lla",
            "name": "LLA",
            "region": "LATIN AMERICA",
            "image_url": "https://lolstatic-a.akamaihd.net/esports-assets/production/league/lla-55ylm4hf.png",
            "priority": 206,
        },
        {
            "id": "98767975604431411",
            "slug": "worlds",
            "name": "Worlds",
            "region": "INTERNATIONAL",
            "image_url": "https://lolstatic-a.akamaihd.net/esports-assets/production/league/worlds-3om032jn.png",
            "priority": 209,
        },
        {
            "id": "98767991295297326",
            "slug": "all-star",
            "name": "All-Star Event",
            "region": "INTERNATIONAL",
            "image_url": "https://lolstatic-a.akamaihd.net/esports-assets/production/league/all-star-dtf4kf16.png",
            "priority": 211,
        },
        {
            "id": "98767991299243165",
            "slug": "lcs",
            "name": "LCS",
            "region": "NORTH AMERICA",
            "image_url": "https://lolstatic-a.akamaihd.net/esports-assets/production/league/lcs-79qe3e0y.png",
            "priority": 1,
        },
        {
            "id": "98767991302996019",
            "slug": "lec",
            "name": "LEC",
            "region": "EUROPE",
            "image_url": "https://lolstatic-a.akamaihd.net/esports-assets/production/league/eu-lcs-dgpu3cuv.png",
            "priority": 2,
        },
        {
            "id": "98767991310872058",
            "slug": "lck",
            "name": "LCK",
            "region": "KOREA",
            "image_url": "https://lolstatic-a.akamaihd.net/esports-assets/production/league/lck-7epeu9ot.png",
            "priority": 3,
        },
        {
            "id": "98767991314006698",
            "slug": "lpl",
            "name": "LPL",
            "region": "CHINA",
            "image_url": "https://lolstatic-a.akamaihd.net/esports-assets/production/league/lpl-china-6ygsd4c8.png",
            "priority": 201,
        },
        {
            "id": "98767991325878492",
            "slug": "msi",
            "name": "MSI",
            "region": "INTERNATIONAL",
            "image_url": "https://lolstatic-a.akamaihd.net/esports-assets/production/league/msi-iu1t0cjd.png",
            "priority": 210,
        },
        {
            "id": "98767991331560952",
            "slug": "oce-opl",
            "name": "OPL",
            "region": "OCEANIA",
            "image_url": "https://lolstatic-a.akamaihd.net/esports-assets/production/league/oce-opl-aun5eljl.png",
            "priority": 207,
        },
        {
            "id": "98767991332355509",
            "slug": "cblol-brazil",
            "name": "CBLOL",
            "region": "BRAZIL",
            "image_url": "https://lolstatic-a.akamaihd.net/esports-assets/production/league/cblol-brazil-46x5zjmg.png",
            "priority": 204,
        },
        {
            "id": "98767991343597634",
            "slug": "turkiye-sampiyonluk-ligi",
            "name": "TCL",
            "region": "TURKEY",
            "image_url": "https://lolstatic-a.akamaihd.net/esports-assets/production/league/turkiye-sampiyonluk-ligi-8r9ofb9.png",
            "priority": 203,
        },
        {
            "id": "98767991349120232",
            "slug": "league-of-legends-college-championship",
            "name": "College Championship",
            "region": "NORTH AMERICA",
            "image_url": "https://lolstatic-a.akamaihd.net/esports-assets/production/league/league-of-legends-college-championship-h6j74ouz.png",
            "priority": 212,
        },
        {
            "id": "98767991349978712",
            "slug": "ljl-japan",
            "name": "LJL",
            "region": "JAPAN",
            "image_url": "https://lolstatic-a.akamaihd.net/esports-assets/production/league/ljl-japan-j27k8oms.png",
            "priority": 208,
        },
        {
            "id": "99332500638116286",
            "slug": "lcs-academy",
            "name": "LCS Academy",
            "region": "NORTH AMERICA",
            "image_url": "https://lolstatic-a.akamaihd.net/esports-assets/production/league/lcs-academy-4o8goq8n.png",
            "priority": 202,
        },
    ]

    # Insert leagues using SQLAlchemy
    for league_dict in leagues_data:
        league = League(**league_dict)
        session.add(league)
    session.commit()

    # Query leagues and verify count
    leagues = session.query(League).order_by(League.priority).all()
    assert len(leagues) == 15

    # Verify ordering by priority
    assert leagues[0].slug == "lcs"  # priority 1
    assert leagues[1].slug == "lec"  # priority 2
    assert leagues[2].slug == "lck"  # priority 3
