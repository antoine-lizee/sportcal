from dateutil import parser
from flask import Flask, render_template, request

print("!! Initializing app.. !!")
app = Flask(__name__)

from data import request_sport_radar, get_teams

teams = get_teams()


@app.template_filter('strftime')
def _jinja2_filter_datetime(date):
    date = parser.parse(date)
    native = date.replace(tzinfo=None)
    format='%a %d %b %H:%M'
    return native.strftime(format)


@app.route("/", methods=['GET', 'POST'])
def index():
    selected_team_values = []
    events = []
    email_address = ""
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
        if 'calendar' in request.form:
            email_address = request.form['email_address']
            print("got calendar request")
    return render_template(
        "index.html",
        teams=teams,
        selected_team_values=selected_team_values,
        events=events,
        email_address=email_address,
    )
