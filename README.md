# SomRPG

SomRPG is a self-hosted text-heavy web RPG inspired by PC-98 and early-2000s menu-driven RPGs. Its main progression is now an original floor-based tower ascent: every floor can introduce a new region, enemies, shop stock and progression gate.

## Stack

- Django 5.2 LTS
- SQLite
- Server-rendered HTML/CSS
- Lightweight JavaScript for bilingual UI, live shell and transient chat
- Gunicorn + WhiteNoise
- Docker
- Optional Discord OAuth for community accounts

## Current milestone — v0.7.0

### Tower ascent

- 20 authored floors form the first tower sector.
- Every floor has its own name, biome, description and market identity.
- Enemy pools are restricted by floor ranges instead of using one universal encounter forever.
- Major progression bosses currently guard Floors 5, 10, 15 and 20.
- Clearing an encounter opens the next floor.
- The Tower screen shows cleared, current and near-future floors.
- Floor discovery is recorded automatically in the Codex.

### Progressive floor shops

Shop progression is tied to the highest floor reached.

- New equipment unlocks at specific floors.
- Previously unlocked stock remains available after climbing higher.
- The initial stock progression spans Floor 1 through Floor 20.
- Shop price and unlock floor are data-driven and editable from Django Admin.
- Buying or spending gold does not reduce the Commerce ranking, which continues to track gross gold earned.

### Character builds and equipment

v0.7.0 introduces the first build layer:

- Vanguard: additional HP and Defense.
- Strider: additional Attack.
- Arcanist: stronger Attack at the cost of HP.
- Equipment slots for weapon, head, body, hands, feet and accessory.
- Only one item can be equipped per slot.
- Gear can roll floor-scaled random affixes when acquired.
- Higher floors make stronger affixes eligible.

These archetypes and affixes are deliberately simple prototypes and can be rebalanced or replaced later.

### Evolvable menu

The left navigation is generated from a central registry instead of being hardcoded into the base template.

- Core ascent features are available immediately.
- City Guard unlocks at Floor 2.
- Workshop unlocks at Floor 3.
- The broader Town systems laboratory unlocks at Floor 5.
- New systems can be added, moved or floor-gated without rebuilding the whole layout.

### Interface

- English and French interface with a persistent FR / EN selector.
- Three-column desktop shell: compact player/menu rail, central game content and authenticated live chat on the right.
- Responsive tablet/mobile layout.
- Static assets are versioned and the browser polls `/api/version/` so running clients reload automatically when SomRPG changes version.

### Live community chat

- Only authenticated accounts can read or send chat messages.
- Chat is transient and is not stored in SQLite.
- A newly connected/refreshed client receives no previous messages.

### Internal clock and daily reset

- Europe/Paris clock displayed in the interface.
- SomRPG's logical day changes at **22:00 Europe/Paris**, including daylight-saving changes.
- Classic daily systems use this reset boundary.

### Core RPG

- Persistent character save
- Floor-based progression and boss gates
- Automated turn-based combat logs
- XP, levels, gold and loot
- Slotted equipment and affixes
- City Guard AFK service with no fixed shift duration
- Workshop crafting
- Passive Codex discovery

### Community event

Discord-connected players can participate in an active community season. Global score combines four normalized categories:

| Category | Measurement | Coefficient |
| --- | --- | ---: |
| Dungeon | Floors cleared during the season | ×1 |
| Commerce | Total gold earned during the season | ×2 |
| Crafting | Crafting XP earned during the season | ×2 |
| Codex | Discovery completion percentage | ×0.5 |

## Classic systems laboratory

The separate `classic` Django app groups broad browser-RPG mechanics so they can be tested, renamed, merged into the main game or removed without dismantling the tower/community core.

Current prototypes include adventures, training, Arena/Honor, market and mounts, Blacksmith, enchantments, Aura, companions, Stronghold/Underworld, guilds and raids, daily rewards/tasks, achievements, Fortune, World Boss and Event Dungeon.

## Discord OAuth

Discord login is optional for local solo play but required for community rankings and live chat.

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

## Docker

```bash
docker compose up --build -d
```

Persistent game data is stored in `./data`. Live chat is intentionally excluded from persistent storage.

## Administration

Django Admin exposes tower floors, bosses, progressive shop offers, core game data, community systems and the `classic` laboratory so content and balancing can evolve without hardcoding every change.

## Branch cleanup

After changes are merged into `main`, the GitHub cleanup workflow removes merged `feat/`, `fix/` and `chore/` branches automatically.
