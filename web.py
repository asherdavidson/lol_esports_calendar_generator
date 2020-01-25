from functools import wraps
from io import BytesIO
from time import time

from flask import Flask, render_template, request, send_file

from datastore import League, CalendarCache

app = Flask(__name__)


def time_route(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        start_time = time()
        result = f(*args, **kwargs)
        end_time = time()
        print(f'{f.__name__} took {end_time - start_time:.8f}s')
        return result

    return wrapper


@app.route('/')
@time_route
def index():
    leagues = League.get_front_page_items()
    template = render_template('index.html', leagues=leagues)

    return template


@app.route('/api/query-leagues')
@time_route
def api_query_leagues():
    leagues = request.args.get('leagues').split(',')

    cal = CalendarCache.get_or_create_calendar(leagues)

    io = BytesIO(cal)
    io.seek(0)

    return send_file(io,
                     attachment_filename='cal.ics',
                     as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
