from io import BytesIO

from flask import Flask, render_template, request, send_file

from calendar_generator import generate_cal, query_leagues
from datastore import League

app = Flask(__name__)


@app.route('/')
def index():
    leagues = League.get_front_page_items()
    template = render_template('index.html', leagues=leagues)

    return template


@app.route('/api/query_leagues')
def api_query_leagues():
    leagues = request.args.get('leagues').split(',')

    query = query_leagues(leagues)
    cal = generate_cal(query)

    io = BytesIO(cal.to_ical())
    io.seek(0)

    return send_file(io,
                     attachment_filename='cal.ics',
                     as_attachment=True)


if __name__ == '__main__':
    app.run(debug=False)
