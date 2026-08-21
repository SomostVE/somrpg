# SomRPG

SomRPG is a self-hosted text-heavy web RPG inspired by PC-98 and early-2000s menu-driven RPGs. The core loop combines dungeon progression, automated turn-based combat, loot, crafting, City Guard AFK work and community rankings.

## Stack

- Django 5.2 LTS
- SQLite
- Server-rendered HTML/CSS
- Gunicorn + WhiteNoise
- Docker
- Optional Discord OAuth for community accounts

## Current milestone — v0.4.0

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

Gold spent never reduces Commerce progress: the ranking tracks gross gold earned, not current wallet balance.

## Classic systems laboratory

Version 0.4.0 adds a separate Django app named `classic`. It deliberately groups broad browser-RPG mechanics in one removable module so each system can be tested, renamed, merged into the core game or deleted later without dismantling the dungeon/community architecture.

The Town currently prototypes:

- regenerating Adventure Points and rotating Adventure Board jobs;
- permanent stat training;
- asynchronous Arena, Honor and win streaks;
- daily Market offers and temporary mounts;
- Blacksmith dismantling and item upgrades;
- Enchantments;
- item sacrifice and persistent Aura;
- recruitable/trainable Companions;
- passive Stronghold resources and an Underworld branch;
- player Guilds, donations, Instructor/Treasure upgrades and Guild Raids;
- daily login rewards, task checklist and Fortune Shrine;
- achievements;
- a shared World Boss;
- a limited Event Dungeon / tower.

The classic layer already feeds selected bonuses back into normal dungeon combat: active companions and enhanced equipment affect combat, while Guild Instructor/Treasure/Raid levels modify dungeon rewards.

## Discord OAuth

Discord login is optional for local solo play but required to enter community rankings.

Configure the OAuth2 redirect URL as:

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

The OAuth scope is limited to `identify`.

## Run with Docker

```bash
docker compose up --build -d
```

Persistent data is stored in `./data`.

## Administration

Django Admin exposes the core game, community systems and the entire `classic` laboratory so values and content can be adjusted without code changes.
