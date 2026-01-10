import os
import requests
from dateutil.parser import parse
from urllib.parse import urlparse

from sqlalchemy import select

from backend.datastore import League, Match, SessionLocal

API_KEY = "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z"  # public API key
HEADERS = {
    "x-api-key": API_KEY,
    "User-Agent": "LOL eSports Parser|https://github.com/asherdavidson/lol_esports_calendar_generator|"
    "asher@asherdavidson.net",
}

LEAGUES_URL = "https://prod-relapi.ewp.gg/persisted/gw/getLeagues?hl=en-US"
MATCHES_URL = "https://prod-relapi.ewp.gg/persisted/gw/getSchedule?hl=en-US"
MATCHES_URL_PAGE_TOKEN = (
    "https://prod-relapi.ewp.gg/persisted/gw/getSchedule?hl=en-US&pageToken={}"
)

# Image storage directory
ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'public', 'assets', 'img')


def league_data():
    r = requests.get(LEAGUES_URL, headers=HEADERS)

    for data in r.json()["data"]["leagues"]:
        yield {
            "id": data["id"],
            "slug": data["slug"],
            "name": data["name"],
            "region": data["region"],
            "image_url": data["image"],
            "priority": data["priority"],
        }


def download_league_image(image_url, slug):
    """Download league image and save it to the assets directory."""
    try:
        # Ensure assets directory exists
        os.makedirs(ASSETS_DIR, exist_ok=True)

        # Download the image
        response = requests.get(image_url, headers=HEADERS)
        response.raise_for_status()

        # Get file extension from URL
        parsed_url = urlparse(image_url)
        file_extension = os.path.splitext(parsed_url.path)[1] or '.png'

        # Save image with league slug as filename
        filename = f"{slug}{file_extension}"
        filepath = os.path.join(ASSETS_DIR, filename)

        with open(filepath, 'wb') as f:
            f.write(response.content)

        print(f"Downloaded image for {slug}: {filename}")
        return True

    except Exception as e:
        print(f"Failed to download image for {slug}: {e}")
        return False


def import_leagues(session):
    print("Importing leagues")
    for data in league_data():
        league = session.get(League, data["id"])
        if league:
            # Update existing league
            for key, value in data.items():
                setattr(league, key, value)
        else:
            # Insert new league
            league = League(**data)
            session.add(league)
    session.commit()

    # Download images for all leagues
    print("Downloading league images")
    stmt = select(League)
    for league in session.scalars(stmt):
        download_league_image(league.image_url, league.slug)


def match_data(json, session):
    for data in json["data"]["schedule"]["events"]:
        if data["type"] == "match":
            league_slug = data["league"]["slug"]
            stmt = select(League).where(League.slug == league_slug)
            league = session.scalar(stmt)

            if not league:
                print(f"Warning: League {league_slug} not found, skipping match")
                continue

            yield {
                "id": data["match"]["id"],
                "start_time": parse(data["startTime"]),
                "block_name": data["blockName"],
                "number_of_matches": data["match"]["strategy"]["count"],
                "team_a": data["match"]["teams"][0]["code"],
                "team_b": data["match"]["teams"][1]["code"],
                "league_id": league.id,
            }


def import_matches_batch(session, json_data):
    """Import a batch of matches from JSON data."""
    for data in match_data(json_data, session):
        match = session.get(Match, data["id"])
        if match:
            # Update existing match
            for key, value in data.items():
                setattr(match, key, value)
        else:
            # Insert new match
            match = Match(**data)
            session.add(match)
    session.commit()


def import_matches(session):
    print("Importing matches")

    r = requests.get(MATCHES_URL, headers=HEADERS)
    import_matches_batch(session, r.json())

    while next_page_token := r.json()["data"]["schedule"]["pages"].get("newer", False):
        print(f"Downloading next page {next_page_token}")
        r = requests.get(
            MATCHES_URL_PAGE_TOKEN.format(next_page_token), headers=HEADERS
        )
        import_matches_batch(session, r.json())

    while last_page_token := r.json()["data"]["schedule"]["pages"].get("older", False):
        print(f"Downloading previous page {last_page_token}")
        r = requests.get(
            MATCHES_URL_PAGE_TOKEN.format(last_page_token), headers=HEADERS
        )
        import_matches_batch(session, r.json())


def import_all():
    session = SessionLocal()
    try:
        import_leagues(session)
        import_matches(session)
    finally:
        session.close()


if __name__ == "__main__":
    import_all()
