from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

try:
    from firebase_service import _db
except Exception:
    _db = lambda: None

PROGRESS_KEYS = {
    "chat": 10,
    "roadmap": 20,
    "skills": 20,
    "opportunities": 15,
    "resources": 15,
    "goal": 10,
    "profile": 10,
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _defaults(user: dict[str, Any]) -> dict[str, Any]:
    return {
        "uid": user.get("uid", ""),
        "name": user.get("name", ""),
        "email": user.get("email", ""),
        "career_goal": "",
        "completed": [],
        "progress": 0,
        "recent_chats": [],
        "created_at": _now(),
        "updated_at": _now(),
    }


def _calculate_progress(completed: list[str]) -> int:
    return min(100, sum(PROGRESS_KEYS.get(item, 0) for item in set(completed)))


def get_profile(user: dict[str, Any]) -> dict[str, Any]:
    profile = _defaults(user)
    db = _db()
    if db is not None and user.get("uid"):
        try:
            data = db.collection("users").document(user["uid"]).get().to_dict() or {}
            profile.update(data)
        except Exception:
            pass
    completed = list(profile.get("completed") or [])
    profile["completed"] = completed
    profile["progress"] = _calculate_progress(completed)
    return profile


def mark_complete(user: dict[str, Any], item: str) -> dict[str, Any]:
    profile = get_profile(user)
    completed = set(profile.get("completed") or [])
    completed.add(item)
    profile["completed"] = sorted(completed)
    profile["progress"] = _calculate_progress(profile["completed"])
    profile["updated_at"] = _now()
    db = _db()
    if db is not None and user.get("uid"):
        try:
            db.collection("users").document(user["uid"]).set(
                {
                    "completed": profile["completed"],
                    "progress": profile["progress"],
                    "updated_at": profile["updated_at"],
                },
                merge=True,
            )
        except Exception:
            pass
    return profile


def set_goal(user: dict[str, Any], goal: str) -> dict[str, Any]:
    profile = get_profile(user)
    profile["career_goal"] = goal.strip()[:500]
    db = _db()
    if db is not None and user.get("uid"):
        try:
            db.collection("users").document(user["uid"]).set(
                {"career_goal": profile["career_goal"], "updated_at": _now()}, merge=True
            )
        except Exception:
            pass
    return mark_complete(user, "goal")


def save_recent_chat(user: dict[str, Any], title: str, prompt: str) -> dict[str, Any]:
    profile = get_profile(user)
    item = {"title": title[:120], "prompt": prompt[:1000], "timestamp": _now()}
    chats = [item] + list(profile.get("recent_chats") or [])
    profile["recent_chats"] = chats[:8]
    db = _db()
    if db is not None and user.get("uid"):
        try:
            db.collection("users").document(user["uid"]).set(
                {"recent_chats": profile["recent_chats"], "updated_at": _now()}, merge=True
            )
        except Exception:
            pass
    return profile
