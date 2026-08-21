import json
import os
import re
import time
from contextlib import contextmanager
from pathlib import Path

import fcntl


CHAT_TTL_SECONDS = 10 * 60
CHAT_MAX_MESSAGES = 100
CHAT_RATE_LIMIT_SECONDS = 1.5


def _chat_path():
    configured = os.getenv("SOMRPG_CHAT_PATH", "").strip()
    if configured:
        return Path(configured)
    base = Path("/dev/shm") if Path("/dev/shm").is_dir() else Path("/tmp")
    return base / "somrpg-live-chat.json"


def _empty_state():
    return {"messages": [], "last_by_user": {}}


def _clean_text(value):
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    return text[:220]


@contextmanager
def _state_file():
    path = _chat_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_suffix(path.suffix + ".lock")
    with lock_path.open("a+", encoding="utf-8") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            try:
                state = json.loads(path.read_text(encoding="utf-8")) if path.exists() else _empty_state()
            except (OSError, ValueError, TypeError):
                state = _empty_state()
            if not isinstance(state, dict):
                state = _empty_state()
            state.setdefault("messages", [])
            state.setdefault("last_by_user", {})
            yield state
            temp = path.with_suffix(path.suffix + ".tmp")
            temp.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
            temp.replace(path)
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def _prune(state, now):
    cutoff = now - CHAT_TTL_SECONDS
    messages = [m for m in state.get("messages", []) if float(m.get("time", 0)) >= cutoff]
    state["messages"] = messages[-CHAT_MAX_MESSAGES:]
    last_by_user = state.get("last_by_user", {})
    state["last_by_user"] = {
        str(user_id): float(timestamp)
        for user_id, timestamp in last_by_user.items()
        if float(timestamp) >= cutoff
    }


def read_messages_since(since=0.0, fresh=False):
    now = time.time()
    with _state_file() as state:
        _prune(state, now)
        if fresh:
            return now, []
        messages = [m for m in state["messages"] if float(m.get("time", 0)) > float(since or 0)]
        return now, messages


def post_message(user_id, display_name, text):
    cleaned = _clean_text(text)
    if not cleaned:
        return False, "empty", None

    now = time.time()
    user_key = str(user_id)
    with _state_file() as state:
        _prune(state, now)
        last = float(state["last_by_user"].get(user_key, 0))
        if now - last < CHAT_RATE_LIMIT_SECONDS:
            return False, "rate", None

        message = {
            "id": f"{int(now * 1000)}-{user_key}",
            "time": now,
            "name": _clean_text(display_name)[:48] or "Player",
            "text": cleaned,
        }
        state["messages"].append(message)
        state["messages"] = state["messages"][-CHAT_MAX_MESSAGES:]
        state["last_by_user"][user_key] = now
        return True, None, message
