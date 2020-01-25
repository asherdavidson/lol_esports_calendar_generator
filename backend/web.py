from datetime import datetime
from io import BytesIO

from flask import render_template, request, send_file

from backend import app
from backend.datastore import League, CalendarCache


@app.route('/')
def index():
    leagues = League.get_front_page_items(date=datetime.now().date())
    template = render_template('index.html', leagues=leagues)

    return template


@app.route('/api/query-leagues')
def api_query_leagues():
    leagues = request.args.get('leagues').split(',')

    cal = CalendarCache.get_calender(leagues)

    io = BytesIO(cal)
    io.seek(0)

    return send_file(io,
                     attachment_filename='cal.ics',
                     as_attachment=True)
