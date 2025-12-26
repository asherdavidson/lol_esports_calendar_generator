import pytest

from backend.datastore import League, sqlite_db, drop_tables, create_tables


@pytest.fixture
def transaction():
    with sqlite_db.transaction() as txn:
        yield txn
        txn.rollback()


@pytest.fixture
def empty_database(transaction):
    drop_tables()
    create_tables()


def test_datastore_league_get_front_page_items(empty_database):
    # check empty db
    leagues = list(League.get_front_page_items())
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

    with sqlite_db.atomic():
        rows_modified = League.insert_many(leagues_data).execute()

    assert rows_modified == 15

    leagues = list(League.get_front_page_items())
    assert len(leagues) == 15
