import json
import datetime as dt
import pytz
from typing import Optional
from fastapi import FastAPI

uk = pytz.timezone('Europe/London')

with open("prayer_times.json", "r") as f:
    prayer_times = json.load(f)

def adjust_for_DST(utc_time):
    if type(utc_time) == str:
        dt_object = dt.datetime.strptime(utc_time,"%H:%M")
        DST_time = dt_object.astimezone(uk)
        return dt.datetime.strftime(DST_time, "%H:%M")
    if type(utc_time) == dict:
        for key, value in utc_time.items():
            utc_time[key] = adjust_for_DST(value)

        return utc_time
    if type(utc_time) == list:
        for i, item in enumerate(utc_time):
            utc_time[i] = adjust_for_DST(item)

        return utc_time


# print(adjust_for_DST("10:24"))
app = FastAPI()

# Today
@app.get("/{location}/today")
def get_today(location: str):
    today = dt.datetime.now(dt.UTC).astimezone(uk)
    return {
        "body": prayer_times[location][today.month-1][today.day-1]
    }

# Tomorrow
@app.get("/{location}/tomorrow")
def get_tomorrow(location: str):
    tomorrow = dt.datetime.now(dt.UTC).astimezone(uk) + dt.timedelta(days=1)
    return {
        "body": prayer_times[location][tomorrow.month-1][tomorrow.day-1]
    }

# Yesterday
@app.get("/{location}/yesterday")
def get_yesterday(location: str):
    yesterday = dt.datetime.now(dt.UTC).astimezone(uk) - dt.timedelta(days=1)
    return {
        "body": prayer_times[location][yesterday.month-1][yesterday.day-1]
    }

# Whole Year
@app.get("/{location}")
def get_year(location: str):
    return {
        "body": prayer_times[location.lower()]
    }

# Whole Month
@app.get("/{location}/{month}")
def get_month(location: str, month: int):
    return {
        "body":prayer_times[location.lower()][month-1]
    }

# Whole Day
@app.get("/{location}/{month}/{day}")
def get_day(location: str, month: int, day: int):
    utc_datetime_str_json_obj = prayer_times[location.lower()][month-1][day-1]


    return {
        "body":prayer_times[location.lower()][month-1][day-1]
    }

# Specific time in day
@app.get("/{location}/{month}/{day}/{time}")
def get_time(location: str, month: int, day: int, time: str):

    utc_datetime_str = prayer_times[location.lower()][month-1][day-1][time.lower()]
    utc_datetime_object = dt.datetime.strptime(utc_datetime_str,"%H:%M")
    london_datetime_object = utc_datetime_object.astimezone(uk)

    return {
        "body": london_datetime_object.strftime("%H:%M")
    }


# /location/month/day
# /location -> give current day
# Time format: 13:59
