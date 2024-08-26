import datetime
import json

with open("prayer_times.json", "r") as f:
    prayer_times = json.load(f)

locations = [
    "aberystwyth",
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
    "swindon"
]

day = datetime.datetime(2024, 3, 31) # This is the first day of BST (2024)
end_date = datetime.datetime(2024, 10, 27) # This is the first day of reverting to GMT (2024)

print("Before:", prayer_times["london"][2][30])
while day != end_date:
    for location in locations:
        daily_times = prayer_times[location][day.month - 1][day.day - 1]
        for timename, time in daily_times.items():
            if timename in ("month", "day"):
                continue
            time = datetime.datetime.strptime(time, "%H:%M")
            new_time = datetime.datetime.strftime(time - datetime.timedelta(hours=1), "%H:%M")
            daily_times[timename] = new_time

    day += datetime.timedelta(days=1)

print("After:", prayer_times["london"][2][30])

with open("adjusted_prayer_times.json", "w") as f:
    json.dump(prayer_times, f)
