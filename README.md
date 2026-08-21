# SomRPG

SomRPG is a self-hosted solo web RPG built around menu-driven dungeon progression, automated turn-based combat, loot, equipment and character growth.

## Vision

- Solo-first dark-fantasy dungeon RPG.
- Responsive on desktop and mobile.
- Progress floor by floor rather than through a real-time world map.
- Automated turn-based battles with readable combat logs.
- Persistent character, XP, gold, inventory and equipment.
- No external API, external account or mandatory third-party service at runtime.

## Stack

- Django 5
- SQLite
- Server-rendered HTML
- Lightweight CSS/JavaScript
- Gunicorn
- Docker

## Current milestone — v0.1.0

The first playable loop contains character creation, stats, floor exploration, automated combat, XP/gold rewards, leveling, loot, equipment, SQLite persistence and Django Admin.

## Run with Docker

```bash
docker compose up --build -d
```

Open `http://localhost:8000`. Persistent data is stored in `./data`.

## Scope

SomRPG intentionally starts without MMO systems, a real-time map, external services or third-party accounts. The project is designed to remain fully self-hostable.
