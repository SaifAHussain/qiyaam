import requests, json
from bs4 import BeautifulSoup

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

url = "https://najaf.org/english/prayer/"

def decode_day(table_row):
    prayer_labels = ["imsaak", "dawn", "sunrise", "noon", "sunset", "maghrib", "midnight"]
    times = reversed(list(map(lambda x: x.string, day.find_all("td")))[:-1])
    return dict(zip(prayer_labels, times))

all_times = {}

for location in locations:
    print(f"Scraping times for {location.capitalize()}")
    all_times[location] = []

    route = url + location
    raw_html = requests.get(route).content
    parsed = BeautifulSoup(raw_html, "html.parser")

    months = parsed.find_all("table", class_="my-table")
    for month in months:
        month_times = []
        for day in month.tbody.find_all("tr"):
            month_times.append(decode_day(day))
        all_times[location].append(month_times)

with open("prayer_times.json", "w") as f:
    json.dump(all_times, f)
