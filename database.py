"""
database.py - Persistent SQLite user database for Aura AI.
Stores registered users, password hashes, and user profiles.
"""
from __future__ import annotations

import hashlib
import hmac
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "aura_users.db"

# Salt for password hashing
SECRET_SALT = b"aura_ai_secure_salt_2026_vector_engine"


def _hash_password(password: str) -> str:
    """Create a secure SHA-256 HMAC hash of the password."""
    return hmac.new(SECRET_SALT, password.encode("utf-8"), hashlib.sha256).hexdigest()


def get_db_connection() -> sqlite3.Connection:
    """Returns a SQLite connection with dict-like row access."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initializes users and profiles tables if they don't exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'Tech Professional',
                career_goal TEXT DEFAULT '',
                progress INTEGER DEFAULT 20,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def register_user(name: str, email: str, password: str) -> tuple[bool, Optional[dict[str, Any]], str]:
    """
    Registers a new user in SQLite.
    Returns (success, user_dict, error_message).
    """
    init_db()
    name = name.strip()
    email = email.strip().lower()

    if len(name) < 2:
        return False, None, "Name must be at least 2 characters long."
    if "@" not in email or "." not in email:
        return False, None, "Please enter a valid email address."
    if len(password) < 6:
        return False, None, "Password must be at least 6 characters long."

    pw_hash = _hash_password(password)
    now_str = datetime.now(timezone.utc).isoformat()

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO users (name, email, password_hash, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (name, email, pw_hash, now_str, now_str),
            )
            conn.commit()
            user_id = cursor.lastrowid
            
            user_data = {
                "id": user_id,
                "name": name,
                "email": email,
                "role": "Tech Professional",
                "career_goal": "",
                "progress": 20,
                "created_at": now_str,
            }
            return True, user_data, ""
    except sqlite3.IntegrityError:
        return False, None, "An account with this email already exists. Please log in."
    except Exception as e:
        return False, None, f"Registration error: {str(e)}"


def authenticate_user(email: str, password: str) -> tuple[bool, Optional[dict[str, Any]], str]:
    """
    Verifies user credentials against SQLite.
    Returns (success, user_dict, error_message).
    """
    init_db()
    email = email.strip().lower()
    if not email or not password:
        return False, None, "Email and password are required."

    pw_hash = _hash_password(password)

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()

            if not row:
                return False, None, "Account not found. Please register first."

            if row["password_hash"] != pw_hash:
                return False, None, "Invalid email or password."

            user_data = {
                "id": row["id"],
                "name": row["name"],
                "email": row["email"],
                "role": row["role"],
                "career_goal": row["career_goal"],
                "progress": row["progress"],
                "created_at": row["created_at"],
            }
            return True, user_data, ""
    except Exception as e:
        return False, None, f"Authentication error: {str(e)}"


def get_user_by_id(user_id: int) -> Optional[dict[str, Any]]:
    """Retrieves user profile by ID."""
    init_db()
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return {
                    "id": row["id"],
                    "name": row["name"],
                    "email": row["email"],
                    "role": row["role"],
                    "career_goal": row["career_goal"],
                    "progress": row["progress"],
                    "created_at": row["created_at"],
                }
    except Exception:
        pass
    return None


# Initialize on import
init_db()
