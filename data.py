import json
import os
from datetime import datetime
from pprint import pprint
from time import sleep, time

import requests
from dateutil.relativedelta import relativedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB

from sc_app import app

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgres://localhost/sportcal')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class QueryResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    query_identifier = db.Column(db.String(255), index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    result = db.Column(JSONB)

db.create_all()


API_KEY = "ha3v5v65eexxag3av2hnuhwq"
REFRESH_PERIOD = relativedelta(days=1)
BASE_URL = "https://api.sportradar.us/soccer-xt3/eu/en/%s.json?api_key={}".format(API_KEY)


def request_sport_radar(query_identifier):
    t0 = time()
    existing_query_result = QueryResult.query.\
        filter(QueryResult.query_identifier == query_identifier).\
        order_by(QueryResult.created_at.desc()).\
        first()
    if existing_query_result and existing_query_result.created_at > datetime.utcnow() - REFRESH_PERIOD:
        print("Loading result from request cache for:  '%s'" % query_identifier)
        result = existing_query_result.result
    else:
        resp_txt = requests.get(BASE_URL % query_identifier).text
        if resp_txt[0] != '{':
            print("Problem while querying from API for '%s'. Here is the result:\n%s" % (query_identifier, resp_txt[:100]))
            return {}
        print("Requesting from API for:  '%s'" % query_identifier)
        result = json.loads(resp_txt)
        query_result = QueryResult(query_identifier=query_identifier, result=result)
        db.session.add(query_result)
        db.session.commit()
        sleep(max(1 - (time() - t0), 0))
    return result


def get_teams():
    tournament_list = request_sport_radar('tournaments')['tournaments']
    tournaments_to_be_scanned = {tournament['name']: tournament['id'] for tournament in tournament_list}
    print("Scanning %d tournaments for gathering teams:" % len(tournaments_to_be_scanned))
    pprint(tournaments_to_be_scanned)

    tournament_data = {
        t: request_sport_radar("tournaments/%s/info" % t_id)
        for (t, t_id) in tournaments_to_be_scanned.items()
    }

    teams = (
        team for data in tournament_data.values() if 'groups' in data for team in data['groups'][-1]['teams']
    )

    teams = list({v['id']: v for v in teams}.values())

    print("Received %d teams." % len(teams))

    return teams
