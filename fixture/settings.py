from os import environ

FIXTURE_URL = environ.get("FIXTURE_URL", "https://apigateway.beinsports.com.tr/api/fixture/rewriteid/current/super-lig")

HOURS_INTERVAL = {
    # script will check matches and past - feature range.(now is 0)
    "feature": environ.get("HOURS_INTERVAL_FEATURE", 1),
    "past": environ.get("HOURS_INTERVAL_PAST", 2)
}

# This is return values.
MATCH_EXIST = "1"
CRUCIAL_MATCH_EXIST = "2"
MATCH_NOT_EXIST = "0"

# Specify big teams as comma seperated string. ex: 318,452,666
# If BIG_TEAMS environment not exist than BIG_TEAMS equals GS, TS, BJK, FB by default
BIG_TEAMS = [int(i) for i in environ.get("BIG_TEAMS", "439,425,2311,4633").split(',')]

SECONDS_IN_DAY = 24 * 60 * 60