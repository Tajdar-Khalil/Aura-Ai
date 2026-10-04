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
    /* Hide Streamlit default chrome */
    #MainMenu, header[data-testid="stHeader"], footer, [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
    }
    .stApp {
        background: #030a1f !important;
    }
    [data-testid="stAppViewContainer"], .main, .block-container {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
    }
    iframe {
        width: 100% !important;
        height: 100vh !important;
        min-height: 100vh !important;
        border: none !important;
        display: block !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. Retrieve GROQ_API_KEY from environment or Streamlit secrets
groq_key = os.getenv("GROQ_API_KEY", "").strip()
if not groq_key or "your_" in groq_key.lower():
    try:
        if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
            groq_key = str(st.secrets["GROQ_API_KEY"]).strip()
    except Exception:
        pass


def get_unified_html(api_key: str) -> str:
    idx_path = BASE_DIR / "index.html"
    dash_path = BASE_DIR / "dashboard.html"
    auth_js_path = BASE_DIR / "static" / "js" / "aura_auth.js"

    idx_html = idx_path.read_text(encoding="utf-8")
    dash_html = dash_path.read_text(encoding="utf-8")
    auth_js = auth_js_path.read_text(encoding="utf-8") if auth_js_path.exists() else ""

    # Inlining avatar
    av_path = BASE_DIR / "assets" / "aura_avatar.jpg"
    if not av_path.exists():
        av_path = BASE_DIR / "aura_avatar.jpg"

    av_uri = "assets/aura_avatar.jpg"
    if av_path.exists():
        av_uri = "data:image/jpeg;base64," + base64.b64encode(av_path.read_bytes()).decode("ascii")

    idx_html = idx_html.replace("assets/aura_avatar.jpg", av_uri).replace("aura_avatar.jpg", av_uri)
    dash_html = dash_html.replace("assets/aura_avatar.jpg", av_uri).replace("aura_avatar.jpg", av_uri)

    # Extract styles
    idx_styles = "\n".join(re.findall(r"<style>([\s\S]*?)</style>", idx_html))
    dash_styles = "\n".join(re.findall(r"<style>([\s\S]*?)</style>", dash_html))

    # Extract index body
    idx_body_match = re.search(r"<body>([\s\S]*?)<script src=[\"']static/js/aura_auth.js[\"']>", idx_html)
    if not idx_body_match:
        idx_body_match = re.search(r"<body>([\s\S]*?)<script>", idx_html)
    idx_body = idx_body_match.group(1) if idx_body_match else ""

    # Extract index scripts
    idx_scripts = "\n".join(re.findall(r"<script>([\s\S]*?)</script>", idx_html))

    # Extract dashboard body
    dash_body_match = re.search(r"<body>([\s\S]*?)<script>", dash_html)
    dash_body = dash_body_match.group(1) if dash_body_match else ""

    # Extract dashboard scripts
    dash_scripts = "\n".join(re.findall(r"<script>([\s\S]*?)</script>", dash_html))

    # SPA routing replacements
    idx_scripts = idx_scripts.replace("window.location.href = 'dashboard.html'", "window.navigateTo('dashboard')")
    dash_scripts = dash_scripts.replace("window.location.href = 'index.html'", "window.navigateTo('home')")
    auth_js = auth_js.replace("window.location.href = 'dashboard.html'", "window.navigateTo('dashboard')")
    auth_js = auth_js.replace("window.location.href = 'index.html'", "window.navigateTo('home')")
    auth_js = auth_js.replace("window.location.href = 'signin.html'", "window.navigateTo('home')")

    dash_body = dash_body.replace('href="index.html"', 'href="javascript:window.navigateTo(\'home\')"')
    idx_body = idx_body.replace('href="dashboard.html"', 'href="javascript:window.navigateTo(\'dashboard\')"')

    unified = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AuraAI | AI Career &amp; Skills Navigator</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
{idx_styles}
{dash_styles}
</style>
</head>
<body>

<div id="viewPublic" style="display: block;">
{idx_body}
</div>

<div id="viewDashboard" style="display: none; height: 100vh; flex-direction: column;">
{dash_body}
</div>

<script>
window.__GROQ_API_KEY__ = "{api_key}";

window.navigateTo = function(target) {{
    const pub = document.getElementById('viewPublic');
    const dash = document.getElementById('viewDashboard');
    if (target === 'dashboard') {{
        if (pub) pub.style.display = 'none';
        if (dash) {{
            dash.style.display = 'flex';
            dash.style.flexDirection = 'column';
            dash.style.height = '100vh';
            dash.style.overflow = 'hidden';
        }}
        window.scrollTo(0, 0);
        if (window.AuraAuth && window.AuraAuth.initDashboard) {{
            window.AuraAuth.initDashboard();
        }}
    }} else {{
        if (dash) dash.style.display = 'none';
        if (pub) {{
            pub.style.display = 'block';
        }}
        window.scrollTo(0, 0);
        if (window.AuraAuth && window.AuraAuth.updatePublicHeader) {{
            window.AuraAuth.updatePublicHeader();
        }}
    }}
}};
</script>

<script>
{auth_js}
</script>

<script>
{idx_scripts}
</script>

<script>
{dash_scripts}
</script>

<script>
document.addEventListener('DOMContentLoaded', function() {{
    const user = (window.AuraAuth && window.AuraAuth.getUser) ? window.AuraAuth.getUser() : null;
    const params = new URLSearchParams(window.location.search);
    if (params.get('page') === 'dashboard' || (user && user.name && params.get('page') !== 'home')) {{
        window.navigateTo('dashboard');
    }} else {{
        window.navigateTo('home');
    }}
}});
</script>
</body>
</html>
"""
    return unified


app_html = get_unified_html(groq_key)
components.html(app_html, height=1000, scrolling=True)
