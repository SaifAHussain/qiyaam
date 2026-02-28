# Qiyaam

Shia prayer times API for 35 UK cities, sourced from the [Imam Ali Foundation](https://najaf.org/english/).

**[qiyaam.com](https://qiyaam.com)**

## API

```
GET /{city}/today
GET /{city}/tomorrow
GET /{city}/{month}/{day}
GET /{city}/calendar.ics
```

Example: `https://qiyaam.com/london/today`

## Cities

Aberystwyth, Bangor (Wales), Birmingham, Bournemouth, Brighton, Bristol, Cambridge, Cardiff, Dover, Dundee, Edinburgh, Exeter, Glasgow, Hull, Leeds, Leicester, Liverpool, London, Luton, Manchester, Middlesbrough, Milton Keynes, Newcastle, Norwich, Nottingham, Oxford, Peterborough, Plymouth, Portsmouth, Sheffield, Southampton, Southend-on-Sea, Stoke-on-Trent, Swansea, Swindon

## iPhone Shortcut

[Add to Shortcuts](https://www.icloud.com/shortcuts/568c3e7df9e6495083735671fc4229cd) (London only — edit for other cities)

## Calendar

Subscribe to prayer times:
- Apple: `webcal://qiyaam.com/{city}/calendar.ics?days=365`
- Google: Add by URL → `https://qiyaam.com/{city}/calendar.ics?days=365`
