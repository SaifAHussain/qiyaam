import json
import datetime as dt
from zoneinfo import ZoneInfo
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, conint, Field
from typing import Literal

PRAYER_LABELS = Literal["imsaak", "dawn", "sunrise", "noon", "sunset", "maghrib", "midnight"]

LOCATIONS = Literal["aberystwyth",
    "bangor-wales",
    "birmingham",
    "bournemouth",
    "brighton",
    "bristol",
    "cambridge",
    "cardiff",
    "dover",
    "dundee",
    "edinburgh",
    "exeter",
    "glasgow",
    "hull",
    "leeds",
    "leicester",
    "liverpool",
    "london",
    "luton",
    "manchester",
    "middlesbrough",
    "milton-keynes",
    "newcastle",
    "norwich",
    "nottingham",
    "oxford",
    "peterborough",
    "plymouth",
    "portsmouth",
    "sheffield",
    "southampton",
    "southend-on-sea",
    "stoke-on-trent",
    "swansea",
    "swindon"]

uk = ZoneInfo("Europe/London")

with open("prayer_times.json", "r") as f:
    prayer_times = json.load(f)

#Here we are setting the types and constraints on the data inputs:
class DateModel(BaseModel):
    month: conint(ge=1, le=12)
    day: conint(ge=1, le=31)
    year: conint(ge=1900, le=3000) = Field(default_factory=lambda: dt.datetime.now().year)



class PrayerLabelModel(BaseModel):
    time: PRAYER_LABELS


class LocationModel(BaseModel):
    location: LOCATIONS




# Use a leap year for DST calculations to handle Feb 29
DST_REFERENCE_YEAR = 2024

def adjust_for_DST(utc_time, use_24_hour: bool, year=None, month=None, day=None):
    # Structure: Dictionary with locations as keys, values being a year which is a list of lists (months) containing dictionaries (days) which contain strings (times)
    
    if isinstance(utc_time, str):
        if year is None:
            year = DST_REFERENCE_YEAR

        assert month is not None and day is not None
        dt_object = dt.datetime.strptime(utc_time, "%H:%M").replace(year=year, month=month, day=day, tzinfo=dt.UTC)
        DST_time = dt_object.astimezone(uk)
        time_format = "%H:%M" if use_24_hour else "%I:%M %p"
        return dt.datetime.strftime(DST_time, time_format)


    if isinstance(utc_time, dict):
        utc_time = utc_time.copy()
        for key, value in utc_time.items():
            if key in ["month", "day"]:
                continue
            utc_time[key] = adjust_for_DST(value, use_24_hour, year, utc_time["month"], utc_time["day"])
        return utc_time

    if isinstance(utc_time, list):
        utc_time = utc_time.copy()
        for i, item in enumerate(utc_time):
            utc_time[i] = adjust_for_DST(item, use_24_hour, year)
        return utc_time


app = FastAPI()

VALID_PRAYER_LABELS = ["imsaak", "dawn", "sunrise", "noon", "sunset", "maghrib", "midnight"]

# Calendar feed settings
CALENDAR_EVENTS = [
    ("dawn", "sunrise", "Dawn"),
    ("noon", "sunset", "Noon"),
    ("maghrib", "midnight", "Maghrib"),
]
CALENDAR_DAYS = 30

def get_prayer_datetime(location: str, year: int, month: int, day: int, prayer: str) -> dt.datetime:
    """Get a prayer time as a timezone-aware datetime in UK time."""
    time_str = prayer_times[location][month - 1][day - 1][prayer]
    time_obj = dt.datetime.strptime(time_str, "%H:%M")
    return time_obj.replace(year=year, month=month, day=day, tzinfo=dt.UTC).astimezone(uk)

def generate_ics(location: str, days: int = CALENDAR_DAYS) -> str:
    """Generate an ICS calendar feed for the given location."""
    now = dt.datetime.now(dt.UTC)
    dtstamp = now.strftime("%Y%m%dT%H%M%SZ")
    
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Qiyaam//Prayer Times//EN",
        f"X-WR-CALNAME:Prayer Times - {location.title()}",
    ]
    
    today = dt.datetime.now(uk)
    
    for i in range(days):
        current = today + dt.timedelta(days=i)
        year, month, day = current.year, current.month, current.day
        
        # Skip Feb 29 if data doesn't have it
        if month == 2 and day == 29:
            try:
                _ = prayer_times[location][1][28]  # Check if Feb 29 exists
            except IndexError:
                continue
        
        for start_prayer, end_prayer, summary in CALENDAR_EVENTS:
            start_dt = get_prayer_datetime(location, year, month, day, start_prayer)
            end_dt = get_prayer_datetime(location, year, month, day, end_prayer)
            
            start_str = start_dt.strftime("%Y%m%dT%H%M%S")
            end_str = end_dt.strftime("%Y%m%dT%H%M%S")
            uid = f"{start_prayer}-{current.strftime('%Y-%m-%d')}@qiyaam.com"
            
            lines.extend([
                "BEGIN:VEVENT",
                f"UID:{uid}",
                f"DTSTAMP:{dtstamp}",
                f"DTSTART;TZID=Europe/London:{start_str}",
                f"DTEND;TZID=Europe/London:{end_str}",
                f"SUMMARY:{summary}",
                "END:VEVENT",
            ])
    
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)

def validate_location(location: str) -> str:
    location = location.lower()
    if location not in prayer_times:
        raise HTTPException(status_code=404, detail=f"Location '{location}' not found")
    return location

def validate_month(month: int) -> None:
    if not 1 <= month <= 12:
        raise HTTPException(status_code=400, detail=f"Month must be between 1 and 12")

def validate_day(month: int, day: int) -> None:
    days_in_month = len(prayer_times["london"][month - 1])
    if not 1 <= day <= days_in_month:
        raise HTTPException(status_code=400, detail=f"Day must be between 1 and {days_in_month} for month {month}")

def validate_prayer_label(time: str) -> str:
    time = time.lower()
    if time not in VALID_PRAYER_LABELS:
        raise HTTPException(status_code=400, detail=f"Invalid prayer time '{time}'. Valid options: {', '.join(VALID_PRAYER_LABELS)}")
    return time

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

# Calendar feed (must be before /{location}/{month} to avoid routing conflict)
@app.get("/{location}/calendar.ics")
def get_calendar(location: str, days: int = CALENDAR_DAYS):
    location = validate_location(location)
    ics_content = generate_ics(location, days)
    return Response(content=ics_content, media_type="text/calendar")

# Whole Year
@app.get("/{location}")
def get_year(location: str, use_24_hour: bool = True):
    location = validate_location(location)
    return adjust_for_DST(prayer_times[location], use_24_hour)

# Whole Month
@app.get("/{location}/{month}")
def get_month(location: str, month: int, use_24_hour: bool = True):
    location = validate_location(location)
    validate_month(month)
    return adjust_for_DST(prayer_times[location][month-1], use_24_hour)

# Whole Day
@app.get("/{location}/{month}/{day}")
def get_day(location: str, month: int, day: int, use_24_hour: bool = True):
    location = validate_location(location)
    validate_month(month)
    validate_day(month, day)
    return adjust_for_DST(prayer_times[location][month-1][day-1], use_24_hour)

# Specific time in day
@app.get("/{location}/{month}/{day}/{time}")
def get_time(location: str, month: int, day: int, time: str, use_24_hour: bool = True):
    location = validate_location(location)
    validate_month(month)
    validate_day(month, day)
    time = validate_prayer_label(time)
    return {
        time: adjust_for_DST(prayer_times[location][month-1][day-1][time], use_24_hour, None, month, day)
    }

# TODO:
# Error catching: invalid input (location, month, day, time)
# Location has to be from the list of valid locations
# Prayer label needs to be from the list of valid prayer labels
# Day needs to be 1 <= day <= 31
# Month needs to be 1 <= month <= 12
# Year should probably be 1900 <= year <= 3000
# Pydantic will be used to validate these data objects...

#TODO:
# - Create date validations - a combo of the 31st of feb can't be accepted...
