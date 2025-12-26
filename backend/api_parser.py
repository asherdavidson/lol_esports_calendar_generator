import os
import requests
from dateutil.parser import parse
from urllib.parse import urlparse

from .datastore import League, Match, drop_tables, create_tables, sqlite_db

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
        id = data["id"]
        slug = data["slug"]
        name = data["name"]
        region = data["region"]
        image_url = data["image"]
        priority = data["priority"]

        yield {
            League.id: id,
            League.slug: slug,
            League.name: name,
            League.region: region,
            League.image_url: image_url,
            League.priority: priority,
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


def import_leagues():
    print("Importing leagues")
    League.replace_many(league_data()).execute()
    
    # Download images for all leagues
    print("Downloading league images")
    for league in League.select():
        download_league_image(league.image_url, league.slug)


def match_data(json):
    for data in json["data"]["schedule"]["events"]:
        if data["type"] == "match":
            id = data["match"]["id"]
            start_time = parse(data["startTime"])
            block_name = data["blockName"]
            number_of_matches = data["match"]["strategy"]["count"]
            team_a = data["match"]["teams"][0]["code"]
            team_b = data["match"]["teams"][1]["code"]

            league_slug = data["league"]["slug"]
            league = League.get(League.slug == league_slug)

            yield {
                Match.id: id,
                Match.start_time: start_time,
                Match.block_name: block_name,
                Match.number_of_matches: number_of_matches,
                Match.team_a: team_a,
                Match.team_b: team_b,
                Match.league: league,
            }


def import_matches():
    print("Importing matches")

    r = requests.get(MATCHES_URL, headers=HEADERS)
    Match.replace_many(match_data(r.json())).execute()

    while next_page_token := r.json()["data"]["schedule"]["pages"].get("newer", False):
        print(f"Downloading next page {next_page_token}")
        r = requests.get(
            MATCHES_URL_PAGE_TOKEN.format(next_page_token), headers=HEADERS
        )
        Match.replace_many(match_data(r.json())).execute()

    while last_page_token := r.json()["data"]["schedule"]["pages"].get("older", False):
        print(f"Downloading previous page {last_page_token}")
        r = requests.get(
            MATCHES_URL_PAGE_TOKEN.format(last_page_token), headers=HEADERS
        )
        Match.replace_many(match_data(r.json())).execute()


def import_all():
    with sqlite_db.atomic():
        import_leagues()
        import_matches()


if __name__ == "__main__":
    import_all()
