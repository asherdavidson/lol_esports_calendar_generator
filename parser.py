from datetime import timezone

import requests
from dateutil import parser

from datastore import Tournament, session_scope, League, Bracket, Match, Team, Roster

SCHEDULE_ITEMS_URL = 'http://api.lolesports.com/api/v1/scheduleItems?leagueId={}'
LEAGUES_URL = 'http://api.lolesports.com/api/v1/leagues?id={}'


def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)


def import_league_data(league_id):
    with session_scope() as s:
        league = s.query(League) \
            .filter(League.id == league_id) \
            .one()

        r = requests.get(SCHEDULE_ITEMS_URL.format(league.id))
        json = r.json()

        tournaments = json.get('highlanderTournaments')
        for tournament_data in tournaments:
            id = tournament_data.get('id')
            title = tournament_data.get('title')
            description = tournament_data.get('description')

            tournament = Tournament.create_or_update(s, id,
                                                     title=title,
                                                     description=description,
                                                     league_id=league.id)

            rosters = tournament_data.get('rosters')
            for roster_id in rosters:
                roster_data = rosters.get(roster_id)

                id = int(roster_data.get('team'))
                acronym = roster_data.get('name')

                team = Team.create_or_update(s, id,
                                             acronym=acronym)

                id = roster_data.get('id')
                name = roster_data.get('name')

                Roster.create_or_update(s, id,
                                        tournament=tournament,
                                        name=name,
                                        team=team)

            brackets = tournament_data.get('brackets')
            for bracket_id in brackets:
                bracket_data = brackets[bracket_id]

                id = bracket_data.get('id')
                name = bracket_data.get('name')
                position = bracket_data.get('position')
                group_position = bracket_data.get('groupPosition')
                group_name = bracket_data.get('groupName')

                bracket = Bracket.create_or_update(s, id,
                                                   league=league,
                                                   tournament=tournament,
                                                   name=name,
                                                   position=position,
                                                   group_position=group_position,
                                                   group_name=group_name)

                matches = bracket_data.get('matches')
                for id in matches:
                    match_data = matches[id]

                    id = match_data.get('id')
                    name = match_data.get('name')
                    # scheduled_time =
                    num_matches = len(match_data.get('games'))
                    position = match_data.get('position')
                    group_position = match_data.get('groupPosition')
                    roster_a_id = match_data.get('input')[0].get('roster')
                    roster_a = s.query(Roster).filter(Roster.id == roster_a_id).one()
                    roster_b_id = match_data.get('input')[1].get('roster')
                    roster_b = s.query(Roster).filter(Roster.id == roster_b_id).one()

                    Match.create_or_update(s, id,
                                           league=league,
                                           tournament=tournament,
                                           bracket=bracket,
                                           name=name,
                                           # scheduled_time =
                                           num_matches=num_matches,
                                           position=position,
                                           group_position=group_position,
                                           roster_a_id=roster_a_id,
                                           roster_a=roster_a,
                                           roster_b_id=roster_b_id,
                                           roster_b=roster_b)

        teams_data = json.get('teams')
        for team_data in teams_data:
            id = team_data.get('id')
            slug = team_data.get('slug')
            name = team_data.get('name')

            Team.create_or_update(s, id,
                                  slug=slug,
                                  name=name)

        schedule_items = json.get('scheduleItems')
        for match_data in schedule_items:
            id = match_data.get('match')
            if id:
                scheduled_time = parser.parse(match_data.get('scheduledTime'))
                block_label = match_data.get('tags').get('blockLabel')
                sub_block_label = match_data.get('tags').get('subBlockLabel')
                block_prefix = match_data.get('tags').get('blockPrefix')
                sub_block_prefix = match_data.get('tags').get('subBlockPrefix')

                Match.create_or_update(s, id,
                                       scheduled_time=scheduled_time,
                                       block_label=block_label,
                                       sub_block_label=sub_block_label,
                                       block_prefix=block_prefix,
                                       sub_block_prefix=sub_block_prefix)


def import_league_information(id):
    r = requests.get(LEAGUES_URL.format(id))
    json = r.json()
    try:
        league_data = json.get('leagues')[0]

        slug = league_data.get('slug')
        name = league_data.get('name')
        region = league_data.get('region')
        logo_url = league_data.get('logoUrl')

        print(id, name)
        with session_scope() as s:
            League.create_or_update(s, id,
                                    slug=slug,
                                    name=name,
                                    region=region,
                                    logo_url=logo_url)

            # league = League.get_or_create(s, id)
            # league.slug = slug
            # league.name = name
            # league.region = region
            # league.logo_url = logo_url
            # slug.add(league)
    except TypeError:
        print(id, 'ERROR')


def import_all_league_information():
    for id in range(2, 3):  # 1 to 70
        import_league_information(id)


if __name__ == '__main__':
    import_all_league_information()

    # with session_scope() as s:
    #     for id, name in s.query(League.id, League.name).all():
    #         print('Importing {} ({})'.format(name, id))
    #         import_league_data(id)

    import_league_data(2)

    # with session_scope() as s:
    #     League.create_or_update(s, 1000, slug='test-slug', name='Best league?', region='your pants')
