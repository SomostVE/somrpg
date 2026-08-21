# SomRPG

SomRPG is a self-hosted text-heavy web RPG inspired by PC-98 and early-2000s menu-driven RPGs. The core loop combines dungeon progression, automated turn-based combat, loot, crafting, City Guard AFK work and community rankings.

## Stack

- Django 5.2 LTS
- SQLite
- Server-rendered HTML/CSS
- Gunicorn + WhiteNoise
- Docker
- Optional Discord OAuth for community accounts

## Current milestone — v0.3.0

### Core RPG

- Character creation and persistent save data
- Floor-based dungeon progression
- Automated turn-based combat logs
- XP, levels, gold, loot and equipment
- City Guard AFK service with no fixed shift duration
- Workshop crafting using Guard supplies and gold
- Passive Codex discovery

### Community event

Discord-connected players can participate in an active community season. The global score is a weighted average of four normalized categories:

| Category | Measurement | Coefficient |
| --- | --- | ---: |
| Dungeon | Floors cleared during the season | ×1 |
| Commerce | Total gold earned during the season | ×2 |
| Crafting | Crafting XP earned during the season | ×2 |
| Codex | Discovery completion percentage | ×0.5 |

Dungeon, Commerce and Crafting are normalized against the current season leader to a 0–100 score. Codex already uses a 0–100 completion percentage. Global points are the weighted average across the four coefficients.

Gold spent never reduces Commerce progress: the ranking tracks gross gold earned, not current wallet balance.

## Discord OAuth

Discord login is optional for local solo play but required to enter community rankings.

Create a Discord application and configure its OAuth2 redirect URL to:

```text
https://YOUR-SOMRPG-DOMAIN/auth/discord/callback/
```

Then provide:

```text
DISCORD_CLIENT_ID=...
DISCORD_CLIENT_SECRET=...
DISCORD_REDIRECT_URI=https://YOUR-SOMRPG-DOMAIN/auth/discord/callback/
DJANGO_ALLOWED_HOSTS=YOUR-SOMRPG-DOMAIN,localhost,127.0.0.1
```

The OAuth scope is limited to `identify`; SomRPG does not request access to Discord messages, servers or contacts.

## Run with Docker

```bash
docker compose up --build -d
```

Persistent data is stored in `./data`.

## Community administration

Django Admin exposes:

- community seasons;
- seasonal progress;
- Discord profiles;
- crafting recipes;
- Codex discoveries;
- enemies, items and characters.

The migration creates an initial active `Founders Season` and two starter crafting recipes.
