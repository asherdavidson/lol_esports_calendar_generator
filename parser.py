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

            tournament = Tournament.get_or_create(s, id)
            tournament.title = title
            tournament.description = description
            tournament.league = league
            s.add(tournament)

            rosters = tournament_data.get('rosters')
            for roster_id in rosters:
                roster_data = rosters.get(roster_id)

                id = int(roster_data.get('team'))
                acronym = roster_data.get('name')

                team = Team.get_or_create(s, id)
                team.acronym = acronym
                s.add(team)

                id = roster_data.get('id')
                name = roster_data.get('name')

                roster = Roster.get_or_create(s, id)
                roster.name = name
                roster.tournament = tournament
                roster.team = team
                s.add(roster)

            brackets = tournament_data.get('brackets')
            for bracket_id in brackets:
                bracket_data = brackets[bracket_id]

                id = bracket_data.get('id')
                name = bracket_data.get('name')
                position = bracket_data.get('position')
                group_position = bracket_data.get('groupPosition')
                group_name = bracket_data.get('groupName')

                bracket = Bracket.get_or_create(s, id)
                bracket.name = name
                bracket.position = position
                bracket.group_position = group_position
                bracket.group_name = group_name
                bracket.tournament = tournament
                s.add(bracket)

                matches = bracket_data.get('matches')
                for match_id in matches:
                    match_data = matches[match_id]

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

                    match = Match.get_or_create(s, id)
                    match.name = name
                    match.num_matches = num_matches
                    match.position = position
                    match.group_position = group_position
                    match.league = league
                    match.tournament = tournament
                    match.bracket = bracket
                    match.roster_a = roster_a
                    match.roster_b = roster_b
                    match.team_a = match.roster_a.team
                    match.team_b = match.roster_b.team
                    s.add(match)

        schedule_items = json.get('scheduleItems')
        for match_data in schedule_items:
            match_id = match_data.get('match')
            if match_id:
                scheduled_time = parser.parse(match_data.get('scheduledTime'))
                block_label = match_data.get('tags').get('blockLabel')
                sub_block_label = match_data.get('tags').get('subBlockLabel')
                block_prefix = match_data.get('tags').get('blockPrefix')
                sub_block_prefix = match_data.get('tags').get('subBlockPrefix')

                match = Match.get_or_create(s, match_id)
                match.scheduled_time = scheduled_time
                match.block_label = block_label
                match.sub_block_label = sub_block_label
                match.block_prefix = block_prefix
                match.sub_block_prefix = sub_block_prefix
                s.add(match)


def import_league_information():
    for i in range(1, 70):
        r = requests.get(LEAGUES_URL.format(i))
        json = r.json()
        try:
            league_data = json.get('leagues')[0]

            slug = league_data.get('slug')
            name = league_data.get('name')
            region = league_data.get('region')
            logo_url = league_data.get('logoUrl')

            print(i, league_data.get('name'))
            with session_scope() as s:
                league = League.get_or_create(s, i)
                league.slug = slug
                league.name = name
                league.region = region
                league.logo_url = logo_url
                s.add(league)
        except TypeError:
            print(i, 'ERROR')


if __name__ == '__main__':
    # import_league_information()

    # with session_scope() as s:
    #     for id, name in s.query(League.id, League.name).all():
    #         print('Importing {} ({})'.format(name, id))
    #         import_league_data(id)

    # import_league_data(1)

    with session_scope() as s:
        League.create_or_update(s, 1000, slug='test-slug', name='Best league?', region='your pants')
