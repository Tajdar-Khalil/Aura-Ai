from __future__ import annotations

import base64
import os
import re
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# 1. Page Configuration
st.set_page_config(
    page_title="AuraAI | AI Career & Skills Navigator",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. Inject CSS to hide all default Streamlit chrome & padding
st.markdown("""
<style>
    #MainMenu, header, footer, [data-testid="stHeader"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
    }
    .main, .block-container {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
    }
    div[data-testid="stVerticalBlock"] {
        gap: 0 !important;
    }
    iframe {
        width: 100% !important;
        border: none !important;
        min-height: 100vh !important;
        display: block !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. Retrieve GROQ_API_KEY
groq_key = os.getenv("GROQ_API_KEY", "").strip()
if not groq_key or "your_" in groq_key.lower():
    try:
        if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
            groq_key = str(st.secrets["GROQ_API_KEY"]).strip()
    except Exception:
        pass

# 4. Determine Active Page
try:
    current_page = st.query_params.get("page", "index").lower()
except Exception:
    current_page = "index"

PAGE_MAP = {
    "index": "index.html",
    "home": "index.html",
    "dashboard": "dashboard.html",
    "signin": "signin.html",
    "login": "signin.html",
    "signup": "signup.html",
    "register": "signup.html",
    "about": "about.html",
    "contact": "contact.html",
}

target_file = PAGE_MAP.get(current_page, "index.html")
html_path = BASE_DIR / target_file
if not html_path.exists():
    html_path = BASE_DIR / "templates" / target_file
if not html_path.exists():
    html_path = BASE_DIR / "index.html"

html_content = html_path.read_text(encoding="utf-8")

# 5. Inline Avatar Image as Base64 Data URI
avatar_path = BASE_DIR / "assets" / "aura_avatar.jpg"
if not avatar_path.exists():
    avatar_path = BASE_DIR / "aura_avatar.jpg"

if avatar_path.exists():
    avatar_b64 = base64.b64encode(avatar_path.read_bytes()).decode("ascii")
    avatar_uri = f"data:image/jpeg;base64,{avatar_b64}"
    html_content = html_content.replace("assets/aura_avatar.jpg", avatar_uri)
    html_content = html_content.replace("aura_avatar.jpg", avatar_uri)

# 6. Inline aura_auth.js script so it executes without separate static server
auth_js_path = BASE_DIR / "static" / "js" / "aura_auth.js"
if auth_js_path.exists():
    auth_js_code = auth_js_path.read_text(encoding="utf-8")
    inline_script = f"<script>\n{auth_js_code}\n</script>"
    html_content = html_content.replace('<script src="static/js/aura_auth.js"></script>', inline_script)
    html_content = html_content.replace("<script src='static/js/aura_auth.js'></script>", inline_script)

# 7. Inject Global Config (Groq API Key + Navigation Bridge)
bridge_script = f"""
<script>
window.__GROQ_API_KEY__ = "{groq_key}";
// Navigation bridge for parent window URL query params
document.addEventListener('DOMContentLoaded', function() {{
    document.querySelectorAll('a').forEach(function(link) {{
        var href = link.getAttribute('href') || '';
        if (href.startsWith('#')) return;
        if (href.endsWith('.html') || href === '/' || href.includes('dashboard') || href.includes('login') || href.includes('signin') || href.includes('signup') || href.includes('register') || href.includes('about') || href.includes('contact')) {{
            link.addEventListener('click', function(e) {{
                var page = '';
                if (href.includes('dashboard')) page = 'dashboard';
                else if (href.includes('signin') || href.includes('login')) page = 'signin';
                else if (href.includes('signup') || href.includes('register')) page = 'signup';
                else if (href.includes('about')) page = 'about';
                else if (href.includes('contact')) page = 'contact';
                else page = 'index';

                if (window.top && window.top !== window) {{
                    e.preventDefault();
                    window.top.location.search = '?page=' + page;
                }}
            }});
        }}
    }});
}});
</script>
"""

if "</head>" in html_content:
    html_content = html_content.replace("</head>", f"{bridge_script}\n</head>")
else:
    html_content = bridge_script + html_content

# 8. Render the Full Modern Glassmorphism Web App in Streamlit
components.html(html_content, height=980, scrolling=True)
