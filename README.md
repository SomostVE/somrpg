# SomRPG

SomRPG is a self-hosted text-heavy web RPG inspired by PC-98 and early-2000s menu-driven RPGs. The core loop combines dungeon progression, automated turn-based combat, loot, crafting, City Guard AFK work and community rankings.

## Stack

- Django 5.2 LTS
- SQLite
- Server-rendered HTML/CSS
- Lightweight JavaScript for bilingual UI, live shell and transient chat
- Gunicorn + WhiteNoise
- Docker
- Optional Discord OAuth for community accounts

## Current milestone — v0.6.0

### Interface

- English and French interface with a persistent FR / EN selector.
- Three-column desktop shell inspired by classic browser RPGs: compact player/menu rail, central game content and authenticated live chat on the right.
- Player status is condensed into a small identity card and resource grid instead of a large status panel.
- Tablet and mobile layouts collapse cleanly to one column.
- Static assets include the SomRPG version in their URL, preventing stale CSS/JS after an update.
- The browser checks `/api/version/` periodically and reloads itself when the running server changes version, removing the need for Ctrl+F5.

### Live community chat

- Only authenticated accounts can read or send chat messages.
- Chat is transient: it is not stored in SQLite and a newly connected/refreshed client receives no previous messages.
- The server only keeps a short-lived in-memory/shared-container buffer so currently connected clients can exchange messages between Gunicorn workers.
- The chat rail becomes a normal stacked panel on tablet/mobile.

### Internal clock and daily reset

- The interface displays the current Europe/Paris clock and a live countdown to the reset.
- SomRPG's logical day changes every day at **22:00 Europe/Paris**, including daylight-saving changes.
- Classic daily systems (daily board, login reward, fortune, shop/adventure rotation and boss hit counters) use this 22:00 reset boundary.

### Release branch cleanup

A GitHub Actions cleanup workflow runs after pushes to `main` and deletes merged `feat/`, `fix/` and `chore/` branches. This keeps only useful work branches instead of accumulating old release branches.

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

The separate Django app named `classic` deliberately groups broad browser-RPG mechanics in one removable module so each system can be tested, renamed, merged into the core game or deleted later without dismantling the dungeon/community architecture.

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

Discord login is optional for local solo play but required to enter community rankings and live chat.

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

Persistent game data is stored in `./data`. Live chat is intentionally excluded from persistent storage.

## Administration

Django Admin exposes the core game, community systems and the entire `classic` laboratory so values and content can be adjusted without code changes.
