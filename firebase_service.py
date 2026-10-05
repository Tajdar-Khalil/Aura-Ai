from __future__ import annotations

import json
from typing import Any

import pyrebase
import requests
import streamlit as st

try:
    import firebase_admin
    from firebase_admin import credentials, firestore, messaging
except ImportError:
    firebase_admin = None
    credentials = None
    firestore = None
    messaging = None

# -----------------------------------------------------------------
# Firebase Web Configuration (public — safe to expose)
def _resolve_firebase_api_key() -> str:
    # 1. Check Streamlit secrets
    try:
        if hasattr(st, "secrets"):
            for k in ["FIREBASE_API_KEY", "firebase_api_key", "FIREBASE_WEB_API_KEY"]:
                if k in st.secrets:
                    val = str(st.secrets[k]).strip()
                    if val and not val.startswith("gsk_"):
                        return val
            if "firebase" in st.secrets:
                fb = st.secrets["firebase"]
                val = str(getattr(fb, "get", lambda k, d="": d)("apiKey", "") or getattr(fb, "get", lambda k, d="": d)("api_key", "")).strip()
                if val and not val.startswith("gsk_"):
                    return val
            for k in ["apiKey", "api_key"]:
                if k in st.secrets:
                    val = str(st.secrets[k]).strip()
                    if val and not val.startswith("gsk_"):
                        return val
    except Exception:
        pass

    # 2. Check environment variables
    import os
    env_k = os.getenv("FIREBASE_API_KEY", "").strip() or os.getenv("FIREBASE_WEB_API_KEY", "").strip()
    if env_k and not env_k.startswith("gsk_"):
        return env_k

    # 3. Default Firebase Web Public API Key (safe client identifier)
    return "AIzaSyDOv6h1H6gbYn8RyYImq-m5OTjvLu9Edc4"

firebase_config = {
    "apiKey": _resolve_firebase_api_key(),
    "authDomain": "aura-c07ad.firebaseapp.com",
    "projectId": "aura-c07ad",
    "storageBucket": "aura-c07ad.firebasestorage.app",
    "messagingSenderId": "422030901114",
    "appId": "1:422030901114:web:c6b0eb3bf6b22d93b160c3",
    "databaseURL": "",
}

AUTH_BASE = "https://identitytoolkit.googleapis.com/v1/accounts"

# -----------------------------------------------------------------
# Pyrebase initialization (for user signup / signin)
# -----------------------------------------------------------------
try:
    _pyrebase_app = pyrebase.initialize_app(firebase_config)
    _pyrebase_auth = _pyrebase_app.auth()
except Exception:
    _pyrebase_auth = None


# -----------------------------------------------------------------
# Firebase Admin initialization (for Firestore + FCM)
# Reads from st.secrets["firebase"] which should be a TOML table
# with the service account fields.
# -----------------------------------------------------------------
def _init_admin() -> bool:
    if firebase_admin is None:
        return False
    if firebase_admin._apps:
        return True

    from pathlib import Path
    json_path = Path(__file__).resolve().parent / "firebase_service_account.json"

    try:
        if json_path.is_file():
            cred = credentials.Certificate(str(json_path))
            firebase_admin.initialize_app(cred)
            return True
        elif hasattr(st, "secrets"):
            sa = None
            if "firebase" in st.secrets or "firebase_service_account" in st.secrets:
                raw_sa = st.secrets["firebase"] if "firebase" in st.secrets else st.secrets["firebase_service_account"]
                sa = dict(raw_sa)
            elif "project_id" in st.secrets and "private_key" in st.secrets:
                sa = {
                    "type": str(st.secrets.get("type", "service_account")),
                    "project_id": str(st.secrets.get("project_id", "")),
                    "private_key_id": str(st.secrets.get("private_key_id", "")),
                    "private_key": str(st.secrets.get("private_key", "")),
                    "client_email": str(st.secrets.get("client_email", "")),
                    "client_id": str(st.secrets.get("client_id", "")),
                    "auth_uri": str(st.secrets.get("auth_uri", "https://accounts.google.com/o/oauth2/auth")),
                    "token_uri": str(st.secrets.get("token_uri", "https://oauth2.googleapis.com/token")),
                    "auth_provider_x509_cert_url": str(st.secrets.get("auth_provider_x509_cert_url", "https://www.googleapis.com/oauth2/v1/certs")),
                    "client_x509_cert_url": str(st.secrets.get("client_x509_cert_url", "")),
                    "universe_domain": str(st.secrets.get("universe_domain", "googleapis.com")),
                }

            if sa:
                if "private_key" in sa and isinstance(sa["private_key"], str):
                    sa["private_key"] = sa["private_key"].replace("\\n", "\n")
                cred = credentials.Certificate(sa)
                firebase_admin.initialize_app(cred)
                return True
    except Exception:
        return False
    return False


def _db():
    """Return a Firestore client or None if admin isn't configured."""
    if not _init_admin():
        return None
    try:
        return firestore.client()
    except Exception:
        return None


# -----------------------------------------------------------------
# Public helpers used by app.py
# -----------------------------------------------------------------
def firebase_available() -> bool:
    """True if the web API key is set (authentication can be attempted)."""
    return bool(firebase_config.get("apiKey"))


def _auth_request(endpoint: str, payload: dict) -> dict:
    """REST call to Firebase Auth — used as a fallback if pyrebase fails."""
    if not firebase_config.get("apiKey"):
        raise RuntimeError("Firebase is not configured.")
    response = requests.post(
        f"{AUTH_BASE}:{endpoint}?key={firebase_config['apiKey']}",
        json=payload,
        timeout=15,
    )
    data = response.json()
    if response.status_code >= 400:
        code = data.get("error", {}).get("message", "Firebase authentication failed.")
        friendly = {
            "EMAIL_EXISTS": "An account with this email already exists.",
            "INVALID_PASSWORD": "Invalid email or password.",
            "EMAIL_NOT_FOUND": "Invalid email or password.",
            "WEAK_PASSWORD": "Password must be at least 6 characters.",
            "TOO_MANY_ATTEMPTS_TRY_LATER": "Too many attempts. Please try again later.",
            "OPERATION_NOT_ALLOWED": "Email/password sign-in is not enabled in Firebase.",
        }.get(code, code)
        raise RuntimeError(friendly)
    return data


def register_user(name: str, email: str, password: str, fcm_token: str = "") -> dict:
    """Create a new user account."""
    if not name.strip():
        raise ValueError("Name is required.")

    if _pyrebase_auth is not None:
        try:
            user = _pyrebase_auth.create_user_with_email_and_password(email, password)
            uid = user["localId"]
            id_token = user["idToken"]
            refresh_token = user.get("refreshToken", "")
        except Exception as exc:
            raise RuntimeError(str(exc))
    else:
        data = _auth_request(
            "signUp",
            {"email": email.strip(), "password": password, "returnSecureToken": True},
        )
        uid = data["localId"]
        id_token = data["idToken"]
        refresh_token = data.get("refreshToken", "")

    profile = {
        "uid": uid,
        "name": name.strip(),
        "email": email.strip(),
        "fcm_token": fcm_token or "",
    }
    db = _db()
    if db is not None:
        try:
            db.collection("users").document(uid).set(profile, merge=True)
        except Exception:
            pass

    return {
        "uid": uid,
        "name": name.strip(),
        "email": email.strip(),
        "id_token": id_token,
        "refresh_token": refresh_token,
    }


def login_user(email: str, password: str) -> dict:
    """Sign an existing user in."""
    if _pyrebase_auth is not None:
        try:
            user = _pyrebase_auth.sign_in_with_email_and_password(email, password)
            uid = user["localId"]
            id_token = user["idToken"]
            refresh_token = user.get("refreshToken", "")
        except Exception as exc:
            raise RuntimeError("Invalid email or password.")
    else:
        data = _auth_request(
            "signInWithPassword",
            {"email": email.strip(), "password": password, "returnSecureToken": True},
        )
        uid = data["localId"]
        id_token = data["idToken"]
        refresh_token = data.get("refreshToken", "")

    name = email.split("@")[0]
    db = _db()
    if db is not None:
        try:
            info = db.collection("users").document(uid).get().to_dict()
            if info and info.get("name"):
                name = info["name"]
        except Exception:
            pass

    return {
        "uid": uid,
        "name": name,
        "email": email.strip(),
        "id_token": id_token,
        "refresh_token": refresh_token,
    }


def send_login_notification(fcm_token: str, display_name: str) -> bool:
    """Send an optional FCM notification on successful login."""
    if not fcm_token or firebase_admin is None or messaging is None:
        return False
    if not _init_admin():
        return False
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title="Aura login successful",
                body=f"Welcome back, {display_name}.",
            ),
            token=fcm_token,
        )
        messaging.send(message)
        return True
    except Exception:
        return False


def send_password_reset(email: str) -> bool:
    """Request a Firebase password-reset email."""
    address = str(email or "").strip()
    if not address:
        raise ValueError("Email is required.")
    data = _auth_request(
        "sendOobCode",
        {"requestType": "PASSWORD_RESET", "email": address},
    )
    return bool(data.get("email") or data.get("kind") == "identitytoolkit#GetOobConfirmationCodeResponse")
