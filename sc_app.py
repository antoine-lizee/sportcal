import json
from pprint import pprint
from time import sleep, time

from dateutil import parser
import requests
from flask import Flask, render_template, request

print("!! Initializing app.. !!")
app = Flask(__name__)


API_KEY = "ha3v5v65eexxag3av2hnuhwq"
base_url = "https://api.sportradar.us/soccer-xt3/eu/en/%s.json?api_key={}".format(API_KEY)


def request_sport_radar(string_identifier):
    t0 = time()
    resp_txt = requests.get(base_url % string_identifier).text
    print(resp_txt[:100])
    resp_txt = resp_txt if resp_txt[0] == '{' else '{}'
    sleep(1 - (time() - t0))
    return json.loads(resp_txt)

# tournaments_data = json.loads(requests.get(base_url % "tournaments").text)
# from pprint import pprint
# pprint([(t['name'], t['id']) for t in tournaments_data['tournaments']])

uefa_cl_data = request_sport_radar("tournaments/sr:tournament:7/info")
PL_data = request_sport_radar("tournaments/sr:tournament:17/info")
L1_data = request_sport_radar("tournaments/sr:tournament:34/info")

teams = uefa_cl_data['groups'][8]['teams'] + PL_data['groups'][0]['teams'] + L1_data['groups'][0]['teams']


@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    date = parser.parse(date)
    native = date.replace(tzinfo=None)
    format='%b %d, %Y %H:%M'
    return native.strftime(format)


@app.route("/", methods=['GET', 'POST'])
def index():
    selected_team_values = []
    if request.method == 'POST':
        print(request.form)
        selected_team_values = request.form.getlist('selected_teams')
        if 'events' in request.form:
            selected_teams = [t for t in teams if t['id'] in selected_team_values]
            events = [
                e for t in selected_team_values for e in request_sport_radar("teams/%s/schedule" % t).get('schedule', [])
            ]
            events.sort(key=lambda e: e['scheduled'])
            print("got event request")
            pprint(events[:10])
        if 'calendar' in request.form:
            print("got calendar request")
    print("DONE")
    return render_template("index.html", teams=teams, selected_team_values=selected_team_values, events=events)
