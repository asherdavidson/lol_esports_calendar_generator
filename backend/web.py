from datetime import datetime
from io import BytesIO

from flask import render_template, request, send_file, abort

from backend import app
from backend.datastore import League


@app.route('/')
def index():
    leagues = League.get_front_page_items(date=datetime.now().date())
    template = render_template('index.html', leagues=leagues)

    return template


@app.route('/api/leagues')
def api_leagues():
    return {
        'leagues': [league.to_dict() for league in League.get_front_page_items(date=datetime.now().date())]
    }


@app.route('/api/query-leagues')
def api_query_leagues():
    leagues = tuple(sorted(request.args.get('leagues', '').split(',')))

    if len(leagues) == 1 and leagues[0] == '':
        return abort(400)

    calendar = League.generate_cal(leagues)

    io = BytesIO(calendar)
    io.seek(0)

    return send_file(io,
                     attachment_filename='cal.ics',
                     as_attachment=True)
