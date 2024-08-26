import json
import datetime as dt
from zoneinfo import ZoneInfo
from fastapi import FastAPI

uk = ZoneInfo("Europe/London")

with open("prayer_times.json", "r") as f:
    prayer_times = json.load(f)

def adjust_for_DST(utc_time, use_24_hour: bool, year=None, month=None, day=None):
    if type(utc_time) == str:
        if year == None:
            year = dt.datetime.now().year

        assert(month is not None and day is not None)
        dt_object = dt.datetime.strptime(utc_time,"%H:%M").replace(year=year, month=month, day=day, tzinfo=dt.UTC)
        DST_time = dt_object.astimezone(uk)
        time_format = "%H:%M" if use_24_hour else "%I:%M %p"
        return dt.datetime.strftime(DST_time, time_format)
    if type(utc_time) == dict:
        utc_time = utc_time.copy()
        for key, value in utc_time.items():
            if key in ["month", "day"]:
                continue
            utc_time[key] = adjust_for_DST(value, use_24_hour, year, utc_time["month"], utc_time["day"])

        return utc_time
    if type(utc_time) == list:
        utc_time = utc_time.copy()
        for i, item in enumerate(utc_time):
            utc_time[i] = adjust_for_DST(item, use_24_hour, year)

        return utc_time


app = FastAPI()

# Today
@app.get("/{location}/today")
def get_today(location: str, use_24_hour: bool = True):
    today = dt.datetime.now(dt.UTC).astimezone(uk)
    return get_day(location, today.month, today.day, use_24_hour)

# Specific time today
@app.get("/{location}/today/{time}")
def get_time_today(location: str, time: str, use_24_hour: bool = True):
    today = dt.datetime.now(dt.UTC).astimezone(uk)
    return get_time(location, today.month, today.day, time, use_24_hour)

# Tomorrow
@app.get("/{location}/tomorrow")
def get_tomorrow(location: str, use_24_hour: bool = True):
    tomorrow = dt.datetime.now(dt.UTC).astimezone(uk) + dt.timedelta(days=1)
    return get_day(location, tomorrow.month, tomorrow.day, use_24_hour)

# Specific time tomorrow
@app.get("/{location}/tomorrow/{time}")
def get_time_tomorrow(location: str, time: str, use_24_hour: bool = True):
    tomorrow = dt.datetime.now(dt.UTC).astimezone(uk) + dt.timedelta(days=1)
    return get_time(location, tomorrow.month, tomorrow.day, time, use_24_hour)

# Yesterday
@app.get("/{location}/yesterday")
def get_yesterday(location: str, use_24_hour: bool = True):
    yesterday = dt.datetime.now(dt.UTC).astimezone(uk) - dt.timedelta(days=1)
    return get_day(location, yesterday.month, yesterday.day, use_24_hour)

# Specific time yesterday
@app.get("/{location}/yesterday/{time}")
def get_time_yesterday(location: str, time: str, use_24_hour: bool = True):
    yesterday = dt.datetime.now(dt.UTC).astimezone(uk) - dt.timedelta(days=1)
    return get_time(location, yesterday.month, yesterday.day, time, use_24_hour)

# Whole Year
@app.get("/{location}")
def get_year(location: str, use_24_hour: bool = True):
    return adjust_for_DST(prayer_times[location.lower()], use_24_hour)

# Whole Month
@app.get("/{location}/{month}")
def get_month(location: str, month: int, use_24_hour: bool = True):
    return adjust_for_DST(prayer_times[location.lower()][month-1], use_24_hour)

# Whole Day
@app.get("/{location}/{month}/{day}")
def get_day(location: str, month: int, day: int, use_24_hour: bool = True):
    return adjust_for_DST(prayer_times[location.lower()][month-1][day-1], use_24_hour)

# Specific time in day
@app.get("/{location}/{month}/{day}/{time}")
def get_time(location: str, month: int, day: int, time: str, use_24_hour: bool = True):
    return {
        time.lower(): adjust_for_DST(prayer_times[location.lower()][month-1][day-1][time.lower()], use_24_hour, None, month, day)
    }
