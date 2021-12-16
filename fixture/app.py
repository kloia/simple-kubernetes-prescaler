from datetime import datetime
from sys import maxsize
import requests
from flask import Flask
from settings import *


app = Flask(__name__)

def get_matches():
    app.logger.info("Getting matches from fixture service")
    matches = requests.get("https://apigateway.beinsports.com.tr/api/fixture/rewriteid/current/super-lig")
    match_data = matches.json()["Data"]

    return match_data


def get_delta_hours(match):
    match_date = match.get("matchDate")
    if match_date == None:
        return maxsize
    try:
        delta = datetime.now() - datetime.fromisoformat(match_date)
        delta_hours = (delta.days * SECONDS_IN_DAY + delta.seconds)/360
    except Exception as e:
        app.logger.exception("An error occured when caculating estimated time to match match id=%s " %match.get("id"))
        delta_hours = maxsize

    return delta_hours


def get_teams_id_of_match(match):
    home_team = match.get("homeTeam")
    home_team_id = None if home_team is None else home_team.get("id")

    away_team = match.get("awayTeam")
    away_team_id = None if away_team is None else away_team.get("id")

    return home_team_id, away_team_id


@app.route("/check_matches")
def check_incoming_matches():
    matches = get_matches()
    
    result = MATCH_NOT_EXIST
    for match in matches:
        delta_hours = get_delta_hours(match)
        if delta_hours < HOURS_INTERVAL["feature"] and delta_hours > HOURS_INTERVAL["past"]*-1:
            home_team_id, away_team_id = get_teams_id_of_match(match)
            
            if home_team_id in BIG_TEAMS or away_team_id in BIG_TEAMS:
                app.logger.info("Crusial match found! Match id: %d" %match.get("id"))
                return CRUCIAL_MATCH_EXIST
            app.logger.info("Match found! Match id: %s" %match.get("id"))
            result = MATCH_EXIST
    return result
