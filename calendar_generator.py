from datetime import datetime

import pytz
from icalendar import Calendar
from sqlalchemy.orm import Query

from datastore import session_scope, Match


def write_cal_to_file(cal, filename):
    with open(filename, 'wb') as f:
        f.write(cal.to_ical())


def generate_cal(s, query, tz) -> Calendar:
    cal = Calendar()
    # cal.add('dtstart', datetime(2017, 1, 1).date())  # TODO
    cal.add('summary', "LoL eSports Calendar")
    cal.add('prodid', '-//LoL eSports Calendar Generator//asherdavidson.net//')
    cal.add('x-wr-calname', "LoL eSports Calendar")

    for match in query:
        # cal.add_component(match.get_ical_event(tz))
        cal.add_component(match.get_ical_event_with_time(tz))

    return cal


def query_leagues_exclude_teams(s, leagues, start_date=datetime(2018, 3, 20)) -> Query:
    """
    example_leagues = {
        2: None,  # 2:   NA LCS
        6: [9, 433, 174, 434],  # 6:   LCK - Champions Korea
    }
    """
    queries = []
    for league_id, teams in leagues.items():
        query = None
        if not teams:  # assume all teams
            query = s.query(Match).filter(Match.league_id == league_id)
        else:
            query = s.query(Match) \
                .filter(Match.league_id == league_id) \
                .filter(Match.team_a_id.in_(teams) | Match.team_b_id.in_(teams))

        query = query.filter(Match.scheduled_time >= start_date)

        queries.append(query)

    query = queries[0].union(*queries[1:])

    query = query.order_by(Match.scheduled_time)

    return query


if __name__ == '__main__':
    with session_scope() as s:
        leagues = {
            1: None,  # 1:   All-Star
            2: None,  # 2:   NA LCS
            3: None,  # 3:   EU LCS
            6: None,  # 6:   LCK - Champions Korea
            9: None,  # 9:   World Championship
            10: None,  # 10: Mid-Season Invitational
            20: None,  # 20: uLoL Campus Series
            21: None,  # 21: BTN Invitational: A University League of Legends Event
            39: None,  # 39: BTN League of Legends
            41: None,  # 41: League of Legends College Championship
            43: None,  # 43: Rift Rivals
            49: None,  # 49: LeagueU
            51: None,  # 51: NA Academy
        }

        query = query_leagues_exclude_teams(s, leagues)

        cal = generate_cal(s, query, pytz.timezone('America/New_York'))
        # cal = generate_cal(s, query=query, tz=pytz.utc)

        write_cal_to_file(cal, 'test.ics')

        print(cal.to_ical())
