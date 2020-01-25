import requests
from dateutil.parser import parse

from datastore import League, Match, drop_tables, create_tables

API_KEY = '0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z'
HEADERS = {
    'x-api-key': API_KEY,
    'User-Agent': 'LOL eSports Parser|https://github.com/asherdavidson/lol_esports_calendar_generator|'
                  'asher@asherdavidson.net'
}

LEAGUES_URL = 'https://prod-relapi.ewp.gg/persisted/gw/getLeagues?hl=en-US'
MATCHES_URL = 'https://prod-relapi.ewp.gg/persisted/gw/getSchedule?hl=en-US'
MATCHES_URL_PAGE_TOKEN = 'https://prod-relapi.ewp.gg/persisted/gw/getSchedule?hl=en-US&pageToken={}'


def league_data():
    r = requests.get(LEAGUES_URL, headers=HEADERS)

    for data in r.json()['data']['leagues']:
        id = data['id']
        slug = data['slug']
        name = data['name']
        region = data['region']
        image_url = data['image']
        priority = data['priority']

        yield {
            League.id: id,
            League.slug: slug,
            League.name: name,
            League.region: region,
            League.image_url: image_url,
            League.priority: priority,
        }


def import_leagues():
    print('Importing leagues')
    League.replace_many(league_data()).execute()


def match_data(json):
    for data in json['data']['schedule']['events']:
        id = data['match']['id']
        start_time = parse(data['startTime'])
        block_name = data['blockName']
        number_of_matches = data['match']['strategy']['count']
        team_a = data['match']['teams'][0]['code']
        team_b = data['match']['teams'][1]['code']

        league_slug = data['league']['slug']
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
    print('Importing matches')

    r = requests.get(MATCHES_URL, headers=HEADERS)
    Match.replace_many(match_data(r.json())).execute()

    while next_page_token := r.json()['data']['schedule']['pages'].get('newer', False):
        print(f'Downloading next page {next_page_token}')
        r = requests.get(MATCHES_URL_PAGE_TOKEN.format(next_page_token), headers=HEADERS)
        Match.replace_many(match_data(r.json())).execute()


def import_all():
    drop_tables()
    create_tables()

    import_leagues()
    import_matches()


if __name__ == '__main__':
    import_all()
