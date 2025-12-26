from datetime import datetime
from io import BytesIO

from flask import Flask, request, send_file, abort

from .datastore import League


app = Flask(__name__)


@app.route("/api/leagues")
def api_leagues():
    return {
        "leagues": [
            league.to_dict()
            for league in League.get_front_page_items(date=datetime.now().date())
        ]
    }


@app.route("/api/query-leagues")
def api_query_leagues():
    valid_leagues = [
        league.slug
        for league in League.get_front_page_items(date=datetime.now().date())
    ]
    cleaned_league_names = set(
        league.strip()
        for league in request.args.get("leagues", "").split(",")
        if league in valid_leagues
    )
    leagues = tuple(sorted(cleaned_league_names))

    if len(leagues) == 1 and leagues[0] == "":
        return abort(400)

    calendar = League.generate_cal(leagues, date=datetime.now().date())

    io = BytesIO(calendar)
    io.seek(0)

    return send_file(io, download_name="cal.ics", as_attachment=True)
