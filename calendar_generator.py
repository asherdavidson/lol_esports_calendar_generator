from icalendar import Calendar

from datastore import Match, League


def write_cal_to_file(cal, filename):
    with open(filename, 'wb') as f:
        f.write(cal.to_ical())


def generate_cal(query) -> Calendar:
    cal = Calendar()
    cal.add('summary', "LoL eSports Calendar")
    cal.add('prodid', '-//LoL eSports Calendar Generator//asherdavidson.net//')
    cal.add('x-wr-calname', "LoL eSports Calendar")

    for match in query:
        cal.add_component(match.get_ical_event_with_time())

    return cal


def query_leagues(leagues):
    return (Match
            .select(Match, League)
            .join(League)
            .where(League.slug.in_(leagues))
            .order_by(Match.start_time))
