import json
from pprint import pprint
from time import sleep

import requests
from flask import Flask, render_template, request

print("!! Initializing app.. !!")
app = Flask(__name__)


API_KEY = "ha3v5v65eexxag3av2hnuhwq"
base_url = "https://api.sportradar.us/soccer-xt3/eu/en/%s.json?api_key={}".format(API_KEY)

# tournaments_data = json.loads(requests.get(base_url % "tournaments").text)
# from pprint import pprint
# pprint([(t['name'], t['id']) for t in tournaments_data['tournaments']])

uefa_cl_data = json.loads(requests.get(base_url % "tournaments/sr:tournament:7/info").text)
sleep(1)
PL_data = json.loads(requests.get(base_url % "tournaments/sr:tournament:17/info").text)
sleep(1)
L1_data = json.loads(requests.get(base_url % "tournaments/sr:tournament:34/info").text)

teams = uefa_cl_data['groups'][8]['teams'] + PL_data['groups'][0]['teams'] + L1_data['groups'][0]['teams']


@app.route("/")
def index():
    return render_template("index.html", teams=teams)


@app.route("/get-schedule", methods=['POST'])
def get_schedule():
    print(request.form)
    pprint(request.form)
    selected_team_values = request.form.getlist('selected_teams')
    selected_teams = [t for t in teams if t['id'] in selected_team_values]

    return render_template("index.html", teams=teams, selected_team_values=selected_team_values, selected_teams=selected_teams)
