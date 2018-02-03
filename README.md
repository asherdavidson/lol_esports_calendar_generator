This project has two components: The parser and the ical generator

The parser parses the official League of Legends eSports API and
stores the results locally in a sqlite database. The parser will
update the data in the database if it exists, or it will create
it.

The ical generator uses the data in the database to generate an
ical file that can be read by all calendar applications
([try adding me to Google Calendar!](https://asherdavidson.net/files/lol.ics)).

The reason the parser saves the data into a database is because
the official api is slow and just bad (it is the worst). Creating
a wrapper around the api simply isn't practical in its current
state.

Future plans for this project:
* Add more query types as needed.
* Create a web api over the query types.
  1. There are functions in `calendar_generator.py` that return
     SQLAlchemy queries, which the calendar generator uses to
     populate the calendar.
  2. The goal is to be able to easily extend the api by simply
     adding new query generator functions, which would then
     be mapped to an api endpoint. This allows us to generate
     calendars with different parameters, i.e.:
     * A calendar with only matches where NA LCS teams plays
       (which includes international tournaments), or
     * A calendar with only NA LCS matches (only regional matches)
       and excludes a specific team
* Create a user friendly site to generate personalized calendars.