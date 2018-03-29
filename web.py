from datetime import datetime
from io import BytesIO
from threading import Thread
from time import sleep

import pytz
from flask import Flask, render_template, request, send_file

from api_parser import import_all_league_data
from calendar_generator import query_leagues_exclude_teams, generate_cal
from datastore import session_scope, League

app = Flask(__name__)


@app.route('/')
def index():
    with session_scope() as s:
        leagues = League.get_front_page_items(s)
        template = render_template('index.html', leagues=leagues)

    return template


@app.route('/api/query_leagues_exclude_teams')
def api_query_leagues_exclude_teams():
    leagues = {}

    for key in request.args:
        if key.isdigit():
            if request.args.get(key):
                leagues[int(key)] = list(map(int, request.args.get(key).split(',')))
            else:
                leagues[int(key)] = None

    with session_scope() as s:
        query = query_leagues_exclude_teams(s, leagues)
        cal = generate_cal(s, query, pytz.timezone('America/New_York'))

        io = BytesIO(cal.to_ical())
        io.seek(0)

    return send_file(io,
                     attachment_filename='cal.ics',
                     as_attachment=True)


def update_loop():
    while True:
        print('Importing league data ({})'.format(datetime.now()))
        import_all_league_data()
        sleep(1 * 24 * 60 * 60)  # 1 day * 24 hr/day * 60 min/hr * 60 s/min


def spawn_updater():
    print('Spawning update thread')
    t = Thread(target=update_loop, daemon=True)
    t.start()


if __name__ == '__main__':
    spawn_updater()
    app.run(debug=True)
