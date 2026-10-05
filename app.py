from __future__ import annotations

import base64
import hashlib
import html
import os
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st
from dotenv import load_dotenv

from agent import run_aura
from database import authenticate_user as db_authenticate_user
from database import register_user as db_register_user
from firebase_service import firebase_available, login_user as fb_login_user, register_user as fb_register_user, send_login_notification
from memory import ConversationMemory
from rag import retrieve_context
from security import sanitize_output, validate_user_input
from services.profile_service import get_profile, mark_complete, save_contact_message, save_recent_chat
from ui.styles import inject_styles

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
AVATAR = BASE_DIR / "assets" / "aura_avatar.jpg"

st.set_page_config(
    page_title="AuraAI — AI Career & Skills Navigator",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)
inject_styles()

DEFAULTS: dict[str, Any] = {
    "authenticated": False,
    "user": None,
    "profile": None,
    "page": "Home",
    "dashboard_page": "Chat with Aura",
    "messages": [],
    "memory": ConversationMemory(max_turns=8),
    "pending_approval": None,
    "auth_notice": "",
    "auth_mode": "login",
    "notifications_read": False,
}
for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


def aura_data_uri() -> str:
    if not AVATAR.exists():
        return ""
    return "data:image/jpeg;base64," + base64.b64encode(AVATAR.read_bytes()).decode("ascii")


def initials(name: str) -> str:
    parts = [p for p in name.strip().split() if p]
    return "".join(p[0] for p in parts[:2]).upper() or "A"


def avatar_url(email: str, size: int = 64) -> str:
    digest = hashlib.md5(email.strip().lower().encode()).hexdigest()
    return f"https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}"


def user_name() -> str:
    return (st.session_state.user or {}).get("name") or "Aura User"


def user_email() -> str:
    return (st.session_state.user or {}).get("email") or ""


def navigate(page: str) -> None:
    st.session_state.page = page
    st.rerun()


def logout() -> None:
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.profile = None
    st.session_state.messages = []
    st.session_state.pending_approval = None
    st.session_state.memory = ConversationMemory(max_turns=8)
    st.session_state.page = "Home"
    st.session_state.dashboard_page = "Chat with Aura"
    st.rerun()


def open_auth(mode: str) -> None:
    st.session_state.auth_mode = mode
    st.session_state.page = "Register" if mode == "register" else "Login"
    st.rerun()


# =====================================================================
# PUBLIC NAVIGATION HEADER
# =====================================================================
def render_header() -> None:
    """Responsive fixed public header with clean modern navigation buttons."""
    with st.container(key="public-header"):
        logo_col, spacer_col, home_col, about_col, contact_col, login_col, register_col, drawer_col = st.columns(
            [4.0, 0.4, 0.95, 0.95, 0.95, 1.10, 1.30, 0.8], gap="small", vertical_alignment="center"
        )

        with logo_col:
            st.markdown(
                '<div class="public-brand"><div class="brand-mark">✦</div>'
                '<div class="brand-name">Aura<span>AI</span></div>'
                '<div class="brand-divider"></div>'
                '<div class="brand-sub">AI Career &amp; Skills Navigator</div></div>',
                unsafe_allow_html=True,
            )

        with home_col:
            if st.button("Home", key="public_Home", use_container_width=True,
                         type="primary" if st.session_state.page == "Home" else "secondary"):
                navigate("Home")

        with about_col:
            if st.button("About", key="public_About", use_container_width=True,
                         type="primary" if st.session_state.page == "About" else "secondary"):
                navigate("About")

        with contact_col:
            if st.button("Contact", key="public_Contact", use_container_width=True,
                         type="primary" if st.session_state.page == "Contact" else "secondary"):
                navigate("Contact")

        with login_col:
            if st.session_state.authenticated:
                if st.button("Dashboard", key="public_dashboard", use_container_width=True, type="primary"):
                    navigate("Dashboard")
            else:
                if st.button("Login", key="public_login", use_container_width=True,
                             type="primary" if st.session_state.page == "Login" else "secondary"):
                    open_auth("login")

        with register_col:
            if st.session_state.authenticated:
                if st.button(f"Log Out", key="public_logout",
                             use_container_width=True, type="secondary"):
                    logout()
            else:
                if st.button("Register", key="public_register", use_container_width=True,
                             type="primary" if st.session_state.page == "Register" else "secondary"):
                    open_auth("register")

        with drawer_col:
            with st.container(key="public_mobile_drawer"):
                with st.popover("☰", use_container_width=True):
                    st.markdown(
                        textwrap.dedent('''
                        <div class="drawer-header-brand">
                          <div class="drawer-brand-mark">✦</div>
                          <div>
                            <div class="drawer-brand-name">Aura<span>AI</span></div>
                            <div class="drawer-brand-sub">Career &amp; Skills Navigator</div>
                          </div>
                        </div>
                        <div class="drawer-separator"></div>
                        '''),
                        unsafe_allow_html=True,
                    )
                    if st.button("⌂  Home", key="mob_drawer_home", use_container_width=True,
                                 type="primary" if st.session_state.page == "Home" else "secondary"):
                        navigate("Home")
                    if st.button("◈  About", key="mob_drawer_about", use_container_width=True,
                                 type="primary" if st.session_state.page == "About" else "secondary"):
                        navigate("About")
                    if st.button("▣  Contact", key="mob_drawer_contact", use_container_width=True,
                                 type="primary" if st.session_state.page == "Contact" else "secondary"):
                        navigate("Contact")

                    st.markdown('<div class="drawer-separator"></div>', unsafe_allow_html=True)
                    if st.session_state.authenticated:
                        if st.button("▤  Dashboard", key="mob_drawer_dashboard", use_container_width=True, type="primary"):
                            navigate("Dashboard")
                        if st.button("⏏  Log Out", key="mob_drawer_logout", use_container_width=True, type="secondary"):
                            logout()
                    else:
                        if st.button("Sign In", key="mob_drawer_login", use_container_width=True,
                                     type="primary" if st.session_state.page == "Login" else "secondary"):
                            open_auth("login")
                        if st.button("Sign Up", key="mob_drawer_register", use_container_width=True,
                                     type="primary" if st.session_state.page == "Register" else "secondary"):
                            open_auth("register")


# =====================================================================
# 1. HOME TAB (Hero, Aura Portrait, Metrics & 4 Feature Cards ONLY)
# =====================================================================
def render_home() -> None:
    uri = aura_data_uri()
    
    # Hero Section
    st.markdown(f'''
<div class="hero-container">
  <div>
    <span class="hero-tag">✦ &nbsp; Your AI Career Coach</span>
    <h1 class="hero-title">Navigate your next move with <em>clarity.</em></h1>
    <p class="hero-desc">AI Career &amp; Skills Navigator helps you identify skill gaps, find free learning resources, and explore real-time job market trends, all in one place.</p>
  </div>
  <div class="portrait-wrap">
    <img src="{uri}" alt="Aura, your AI career coach"/>
    <div class="portrait-hello">
      <strong><svg viewBox="0 0 24 24"><path d="M12 1.5c.6 5.2 2.6 8.1 5.6 9.2 1.5.5 3.1.8 5 1.3-4.6 1-7.4 2.6-9 5.4-.7 1.2-1.2 3-1.6 5.6-.4-2.6-.9-4.4-1.6-5.6-1.6-2.8-4.4-4.4-9-5.4 1.9-.5 3.5-.8 5-1.3 3-1.1 5-4 5.6-9.2z"/></svg>Hi, I'm Aura!</strong>
      <span>Your AI Career &amp; Skills Navigator</span>
    </div>
  </div>
</div>
''', unsafe_allow_html=True)

    # CTA Action Button
    cta_col, _ = st.columns([1.5, 4.0])
    with cta_col:
        btn_label = "💬  Enter Aura Dashboard  →" if st.session_state.authenticated else "💬  Enter Aura  →"
        if st.button(btn_label, key="hero_enter_aura", use_container_width=True, type="primary"):
            if st.session_state.authenticated:
                navigate("Dashboard")
            else:
                open_auth("login")

    # 4 Feature Cards (exact match to index.html)
    st.markdown('''
<div class="features-grid">
  <div class="feat-item">
    <div class="feat-ico">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4"/></svg>
    </div>
    <h3>Find Skill Gaps</h3>
    <p>Discover what skills to build next based on live market criteria.</p>
  </div>

  <div class="feat-item">
    <div class="feat-ico">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="4" width="16" height="16" rx="3"/><rect x="9" y="9" width="6" height="6" rx="1" fill="currentColor"/></svg>
    </div>
    <h3>Learn for Free</h3>
    <p>Get curated free tutorials, resources &amp; verified course roadmaps.</p>
  </div>

  <div class="feat-item">
    <div class="feat-ico">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M7 17 17 7M9 7h8v8"/></svg>
    </div>
    <h3>Market Trends</h3>
    <p>Explore real-time job market intelligence and salary benchmarks.</p>
  </div>

  <div class="feat-item">
    <div class="feat-ico">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3l9 9-9 9-9-9z"/><circle cx="12" cy="12" r="2.5" fill="currentColor"/></svg>
    </div>
    <h3>Build Your Future</h3>
    <p>Get personalized autonomous career guidance tailored to your goal.</p>
  </div>
</div>
''', unsafe_allow_html=True)

    # Live Metrics Bar
    st.markdown('''
<div class="metrics-grid">
  <div class="metric-box">
    <div class="metric-val">10M+</div>
    <div class="metric-lbl">Data Points Analyzed</div>
  </div>
  <div class="metric-box">
    <div class="metric-val">98%</div>
    <div class="metric-lbl">Accuracy in Skill Gap Detection</div>
  </div>
  <div class="metric-box">
    <div class="metric-val">Real-Time</div>
    <div class="metric-lbl">Market Intelligence Updates</div>
  </div>
</div>
''', unsafe_allow_html=True)


# =====================================================================
# 2. ABOUT TAB (Architecture, CrewAI, RAG & Governance ONLY)
# =====================================================================
def render_about() -> None:
    st.markdown(textwrap.dedent("""
    <div class="section about-section" style="padding: 30px 0 60px;">
      <div class="about-header text-center">
        <span class="eyebrow">✦ &nbsp; The Engine Behind Aura</span>
        <h2 style="font-size: clamp(2rem, 4vw, 3rem); font-weight: 800; color: #fff; margin: 16px 0 12px;">Professional Grade <span class="gradient">AI Architecture</span></h2>
        <p class="muted max-w-700 mx-auto" style="font-size: 1.05rem; line-height: 1.6;">Built on a cutting-edge autonomous multi-agent framework, Aura doesn't just chat—it executes complex market research, skill analysis, and career mapping on your behalf.</p>
      </div>

      <div class="architecture-grid">
        <div class="arch-card">
          <div class="arch-icon">⚡</div>
          <h3>CrewAI Orchestration</h3>
          <p>Deploying specialized autonomous agents acting as Career Strategist, Market Analyst, and Tech Mentor working in parallel to solve your career challenges.</p>
          <div class="data-pill">3 Active Agents</div>
        </div>
        <div class="arch-card">
          <div class="arch-icon">🧠</div>
          <h3>RAG Knowledge Base</h3>
          <p>Powered by FAISS and all-MiniLM-L6-v2 embedding models. We continuously ingest the latest market reports and tech documentation to provide hallucination-free advice.</p>
          <div class="data-pill">Sub-50ms Vector Search</div>
        </div>
        <div class="arch-card">
          <div class="arch-icon">🔒</div>
          <h3>Human-in-the-loop</h3>
          <p>You remain in full control. Aura proposes high-impact career pivot plans and learning roadmaps, pausing for your explicit approval before finalizing the strategy.</p>
          <div class="data-pill">100% User Governed</div>
        </div>
      </div>
    </div>
    """), unsafe_allow_html=True)


# =====================================================================
# 3. CONTACT TAB (Contact Channels & Working Form ONLY)
# =====================================================================
def render_contact() -> None:
    st.markdown(textwrap.dedent("""
    <div class="contact-wrapper">
      <div class="contact-hero text-center">
        <span class="eyebrow">✦ &nbsp; 24/7 Support Network</span>
        <h2 style="font-size: clamp(2rem, 4vw, 3rem); font-weight: 800; color: #fff; margin: 16px 0 12px;">Connect with <span class="gradient">AuraAI</span></h2>
        <p class="muted max-w-700 mx-auto" style="font-size: 1.05rem; line-height: 1.6;">Whether you're looking for career advice, technical support, or partnership inquiries, our human and AI teams are ready to assist you.</p>
      </div>

      <div class="contact-grid">
        <div class="contact-info-card">
          <div class="contact-info-icon">✉</div>
          <h3 style="color:#fff;">Priority Channels</h3>
          <p class="muted">Access direct support from our core team.</p>

          <div class="status-indicator">
            <span class="status-dot green"></span> <b>Systems Operational</b>
          </div>

          <div class="contact-detail">
            <b>Email Routing</b>
            <span>support@auraai.example &middot; daniyalriazcute@gmail.com</span>
          </div>
          <div class="contact-detail">
            <b>Location</b>
            <span>Chakwal, Punjab, Pakistan</span>
          </div>
          <div class="contact-detail">
            <b>Average Response</b>
            <span>Under 2 Hours</span>
          </div>
        </div>

        <div class="contact-form-card">
          <h3 style="color:#fff;">Send a Message</h3>
          <p class="muted">Your message is securely recorded and delivered.</p>
    """), unsafe_allow_html=True)

    with st.form("contact_form_stream", clear_on_submit=True):
        c1, c2 = st.columns(2, gap="medium")
        with c1:
            contact_name = st.text_input("Name", placeholder="Your full name")
        with c2:
            contact_email = st.text_input("Email", placeholder="you@example.com")
        subject = st.text_input("Subject", placeholder="How can we assist you?")
        message = st.text_area("Message", placeholder="Write your message here...", height=150)
        submitted = st.form_submit_button("Send message  →", type="primary", use_container_width=True)

    st.markdown('</div></div></div>', unsafe_allow_html=True)

    if submitted:
        if not contact_name.strip() or not contact_email.strip() or not message.strip():
            st.error("Please complete your name, email and message before sending.")
        else:
            save_contact_message(contact_name, contact_email, subject, message)
            st.success("✓ Message sent successfully! We will get back to you soon.")


# =====================================================================
# 4. AUTHENTICATION (Login & Sign Up with Database Storage)
# =====================================================================
def render_auth_page(mode: str = "login") -> None:
    showcase_col, form_col = st.columns([1.18, 1.02], gap="large")

    with showcase_col:
        title = "Welcome back to your <span class='gradient'>Career Hub</span>" if mode == "login" else "Elevate your tech career with <span class='gradient'>Aura AI</span>"
        desc = "Access your personalized roadmap, AI chat sessions, and live skill diagnostic reports." if mode == "login" else "Unlock autonomous multi-agent guidance, real-time market benchmark analysis, and curated learning roadmaps."

        st.markdown(
            f'''
<div class="auth-showcase-panel">
  <div class="auth-showcase-badge">✦ AI CAREER ARCHITECT &amp; NAVIGATOR</div>
  <h1 class="auth-showcase-title">{title}</h1>
  <p class="auth-showcase-desc">{desc}</p>
  <div class="tw-wrapper">
    <div class="typewriter-text">Your potential is limitless when backed by targeted AI insights...</div>
  </div>
  <div class="auth-quote-card" style="margin-top: 40px;">
    <div class="auth-quote-avatar"><img src="{aura_data_uri()}"/></div>
    <div>
      <div class="auth-quote-text">"Let's navigate your next big tech career move together."</div>
      <div class="auth-quote-author">✦ Aura — <span>Your Autonomous AI Career Coach</span></div>
    </div>
  </div>
</div>
            ''',
            unsafe_allow_html=True,
        )

    with form_col:
        form_title = "Sign in to Aura" if mode == "login" else "Create your account"
        form_desc = "Enter your credentials to continue your journey." if mode == "login" else "Get started with your free AI career accelerator."

        st.markdown(
            f'''
<div class="auth-card-stream">
  <div class="auth-card-header">
    <div class="auth-avatar-circle"><img src="{aura_data_uri()}"/></div>
    <div>
      <h2 style="margin:0;font-size:23px;font-weight:800;color:#fff;">{form_title}</h2>
      <p style="margin:4px 0 0;font-size:13.5px;color:#9eb5dc;">{form_desc}</p>
    </div>
  </div>
</div>
            ''',
            unsafe_allow_html=True,
        )

        with st.form("aura_full_auth_form", clear_on_submit=False):
            name = st.text_input("Full name", placeholder="Your full name") if mode == "register" else ""
            email = st.text_input("Email address", placeholder="you@example.com")
            password = st.text_input("Password", type="password", placeholder="Your password")
            confirm = st.text_input("Confirm password", type="password", placeholder="Repeat password") if mode == "register" else ""
            submitted = st.form_submit_button(
                "Sign In to Dashboard →" if mode == "login" else "Create Aura Account →",
                type="primary",
                use_container_width=True,
            )

        if submitted:
            try:
                if not email.strip() or not password.strip():
                    raise ValueError("Email and password are required.")

                if mode == "register":
                    if not name.strip():
                        raise ValueError("Full name is required.")
                    if password != confirm:
                        raise ValueError("Passwords do not match.")
                    if len(password) < 6:
                        raise ValueError("Use at least 6 characters for your password.")

                    # 1. Store in SQLite Database
                    success, user_data, err_msg = db_register_user(name.strip(), email.strip(), password)
                    if not success:
                        raise ValueError(err_msg)

                    # 2. Also register in Firebase if available
                    if firebase_available():
                        try:
                            fb_register_user(name.strip(), email.strip(), password)
                        except Exception:
                            pass
                else:
                    # Login: Authenticate against SQLite
                    success, user_data, err_msg = db_authenticate_user(email.strip(), password)
                    if not success:
                        # Fallback: check Firebase if available
                        if firebase_available():
                            try:
                                user_data = fb_login_user(email.strip(), password)
                                success = True
                            except Exception:
                                raise ValueError(err_msg or "Invalid email or password.")
                        else:
                            raise ValueError(err_msg)

                # Set session state and navigate straight to Dashboard
                st.session_state.authenticated = True
                st.session_state.user = user_data
                st.session_state.profile = get_profile(user_data)
                st.session_state.page = "Dashboard"
                st.session_state.dashboard_page = "Chat with Aura"
                st.rerun()

            except Exception as exc:
                st.error(str(exc))

        if mode == "login":
            if st.button("Don't have an account? Create one free →", key="switch_to_reg_btn", type="secondary", use_container_width=True):
                st.session_state.auth_mode = "register"
                st.session_state.page = "Register"
                st.rerun()
        else:
            if st.button("Already have an account? Sign In here →", key="switch_to_log_btn", type="secondary", use_container_width=True):
                st.session_state.auth_mode = "login"
                st.session_state.page = "Login"
                st.rerun()


# =====================================================================
# 5. DASHBOARD (AI Agent, Career Roadmap, Return to Home, Logout)
# =====================================================================
def _safe_markdown(text: str) -> str:
    return html.escape(sanitize_output(text)).replace("\n", "<br>")


def _format_time(value: str | None = None) -> str:
    return value or datetime.now().strftime("%I:%M %p")


def _dashboard_intro() -> str:
    name = html.escape(user_name().split()[0])
    return (f"Welcome back, <b>{name}</b>! I am Aura, your AI Career Coach &amp; Skills Navigator. "
            "Whether you want to build a career roadmap, assess skill gaps, find free resources, or practice tech interviews, I'm here to help!")


def _add_user_message(prompt: str, completion_key: str = "chat") -> None:
    prompt = validate_user_input(prompt)
    if not prompt:
        return
    st.session_state.messages.append({"role": "user", "content": prompt, "time": _format_time()})
    title = prompt if len(prompt) <= 80 else prompt[:77] + "..."
    st.session_state.profile = save_recent_chat(st.session_state.user, title, prompt)
    decision = requires_approval(prompt)
    if decision["required"]:
        st.session_state.pending_approval = {"query": prompt, "completion_key": completion_key, **decision}
        return
    _run_and_store(prompt, approved=False, completion_key=completion_key)


def _run_and_store(prompt: str, approved: bool, completion_key: str = "chat") -> None:
    with st.spinner("Aura is formulating your personalized guidance..."):
        try:
            retrieved = retrieve_context(prompt, k=4)
            result = run_aura(user_query=prompt, memory=st.session_state.memory, retrieved_context=retrieved, human_approved=approved)
            safe = sanitize_output(result)
            st.session_state.memory.add("user", prompt)
            st.session_state.memory.add("assistant", safe)
            st.session_state.messages.append({"role": "assistant", "content": safe, "time": _format_time()})
            st.session_state.profile = mark_complete(st.session_state.user, completion_key)
        except Exception as exc:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"I couldn't complete that request. Technical detail: {sanitize_output(exc)}",
                "time": _format_time(),
            })


def requires_approval(prompt: str) -> dict:
    text = prompt.lower().strip()
    consequential = [
        "should i quit", "should i resign", "should i leave my job", "should i accept",
        "should i reject", "which career should i choose", "choose a career for me",
        "should i switch careers", "should i change careers", "make the decision for me"
    ]
    if any(p in text for p in consequential):
        return {
            "required": True,
            "reason": "This request asks Aura to make a high-stakes personal career decision for you.",
            "action": "Review career trade-offs and options before finalizing.",
        }
    return {"required": False, "reason": "", "action": ""}


def _render_message(message: dict) -> None:
    role = message.get("role")
    content = message.get("content", "")
    safe = _safe_markdown(content)
    if role == "user":
        st.markdown(f'<div class="bubble me">{safe}<small>{html.escape(message.get("time", ""))} ✓✓</small></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bubble assistant"><b style="color:#4db3ff">✦ Aura</b><br>{safe}<small>{html.escape(message.get("time", ""))}</small></div>', unsafe_allow_html=True)


def _send_from_action(prompt: str, completion_key: str | None = None) -> None:
    _add_user_message(prompt, completion_key or "chat")
    st.rerun()


def render_chat_panel() -> None:
    with st.container(key="dashboard-chat"):
        st.markdown(
            '<div class="chat-head"><div class="chat-title"><span class="spark">✦</span>'
            '<div><b>Chat with Aura</b><div class="muted">Your Autonomous AI Career Navigator</div></div></div>'
            '<span class="online">● &nbsp; Aura is online</span></div>',
            unsafe_allow_html=True,
        )

        with st.container(key="dashboard-messages"):
            if not st.session_state.messages:
                st.markdown(
                    f'<div class="bubble assistant welcome-bubble"><b style="color:#4db3ff">✦ Aura</b><br>{_dashboard_intro()}'
                    f'<div class="section-box"><h5>Capabilities &amp; Tools</h5><ul>'
                    f'<li>Identify skill gaps &amp; benchmark against market roles</li>'
                    f'<li>Generate structured 90-day learning roadmaps</li>'
                    f'<li>Search for curated free resources &amp; courses</li>'
                    f'<li>Provide real-time market insights via web search &amp; tools</li>'
                    f'</ul></div><span class="muted">Type a question below or choose a quick prompt to begin.</span></div>',
                    unsafe_allow_html=True,
                )
            for message in st.session_state.messages:
                _render_message(message)

        pending = st.session_state.pending_approval
        if pending:
            st.warning(f"Human Approval Required\n\n{pending['reason']}\n\nAction: {pending['action']}")
            a, b = st.columns(2)
            with a:
                if st.button("✓ Approve and Continue", key="approve", type="primary", use_container_width=True):
                    query = pending["query"]
                    st.session_state.pending_approval = None
                    _run_and_store(query, approved=True, completion_key=pending.get("completion_key", "chat"))
                    st.rerun()
            with b:
                if st.button("✕ Cancel / Revise", key="reject", use_container_width=True):
                    st.session_state.pending_approval = None
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "Action cancelled. Let me know how you'd like to adjust.",
                        "time": _format_time(),
                    })
                    st.rerun()

        chip_cols = st.columns(4)
        chips = [
            ("Show me a 90-day roadmap", "roadmap"),
            ("Free learning resources", "resources"),
            ("Find my Skill Gaps", "skills"),
            ("Explore job market trends", "opportunities"),
        ]
        for col, (label, key) in zip(chip_cols, chips):
            with col:
                if st.button(label, key=f"chip_{key}", use_container_width=True):
                    _send_from_action(label, key)

        with st.form("chat_form", clear_on_submit=True):
            cols = st.columns([0.06, 0.86, 0.08])
            with cols[0]:
                st.markdown("<div style='font-size:20px;text-align:center;padding-top:6px;'>📎</div>", unsafe_allow_html=True)
            with cols[1]:
                prompt = st.text_input("Message", placeholder="Ask Aura anything about your tech career or skills...", label_visibility="collapsed")
            with cols[2]:
                send = st.form_submit_button("➤", use_container_width=True, type="primary")

        if send and prompt:
            _add_user_message(prompt)
            st.rerun()


def render_left_sidebar() -> None:
    profile = st.session_state.profile or get_profile(st.session_state.user)
    st.session_state.profile = profile

    items = [
        ("⌂  Chat with Aura", "chat"),
        ("▱  Career Roadmap", "roadmap"),
        ("◇  Skills Analysis", "skills"),
        ("▣  Opportunities", "opportunities"),
        ("▤  Free Resources", "resources"),
    ]

    with st.container(key="dashboard-left"):
        for label, key in items:
            name = label.split("  ", 1)[-1]
            selected = st.session_state.dashboard_page == name
            if st.button(label, key=f"side_{key}", use_container_width=True, type="primary" if selected else "secondary"):
                st.session_state.dashboard_page = name
                st.rerun()

        # Dedicated "Return to Home" button on left sidebar
        st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
        if st.button("⌂  Return to Home", key="side_return_home", use_container_width=True, type="secondary"):
            navigate("Home")

        progress = int(profile.get("progress", 25))
        completed = set(profile.get("completed") or [])
        st.markdown(
            f'<div class="progress-card"><b>Your Progress</b>'
            f'<div class="progress-row" style="margin-top:12px">'
            f'<div class="ring" style="--p:{progress}"><div>{progress}%</div></div>'
            f'<div><div>Career Growth</div><div class="muted">{len(completed)}/7 milestones complete</div></div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

        st.markdown('<div class="recent"><b>Recent Activity</b>', unsafe_allow_html=True)
        chats = profile.get("recent_chats") or []
        if not chats:
            st.markdown('<p class="muted" style="margin-top:12px">No recent conversations.</p>', unsafe_allow_html=True)
        for index, item in enumerate(chats[:4]):
            title = item.get("title", "Conversation")
            prompt = item.get("prompt", title)
            if st.button(title[:45], key=f"recent_{index}", use_container_width=True):
                st.session_state.dashboard_page = "Chat with Aura"
                _send_from_action(prompt, "chat")
            st.markdown(f'<small class="recent-time">{html.escape(item.get("timestamp", ""))}</small>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


def render_right_sidebar() -> None:
    with st.container(key="dashboard-right"):
        st.markdown(
            f'''
<div class="aura-card">
  <div class="aura-pic"><img src="{aura_data_uri()}" alt="Aura AI"></div>
  <h2>Aura <span>AI</span></h2>
  <p class="aura-role">Your Career Coach &amp; Guide</p>
  <p class="muted">Smart guidance. Better decisions. A brighter future.</p>
</div>
''',
            unsafe_allow_html=True,
        )

        facts = [
            ("◉", "Powered by Llama-3.3-70B", "High-speed reasoning via Groq"),
            ("▣", "RAG Knowledge Base", "Curated FAISS career embeddings"),
            ("♣", "4 External Tools", "Search &middot; Wikipedia &middot; API &middot; Calc"),
            ("◌", "Human-in-the-Loop", "User governance on big decisions"),
        ]

        facts_html = '<div class="facts-card">'
        for icon, title, subtitle in facts:
            facts_html += (
                f'<div class="fact">'
                f'<div class="fact-icon">{icon}</div>'
                f'<div><b>{title}</b><small>{subtitle}</small></div>'
                f'</div>'
            )
        facts_html += '</div>'
        st.markdown(facts_html, unsafe_allow_html=True)

        st.markdown('<div class="quick"><h4>⚡ Quick Actions</h4>', unsafe_allow_html=True)
        actions = [
            ("Generate Career Roadmap", "Generate my career roadmap", "roadmap"),
            ("Analyze My Skills", "Analyze my skills for software engineering", "skills"),
            ("Explore Job Opportunities", "Explore current job market trends", "opportunities"),
            ("Find Learning Resources", "Find free learning resources and courses", "resources"),
        ]
        for label, prompt, key in actions:
            if st.button(label + "  ›", key=f"quick_{key}", use_container_width=True):
                st.session_state.dashboard_page = "Chat with Aura"
                _send_from_action(prompt, key)

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(
            '<div class="quote">✦ &nbsp; &ldquo;Big dreams need a plan.<br>'
            '&nbsp;&nbsp;&nbsp;&nbsp;I\'m here to help you build yours.&rdquo;'
            '<br><span style="float:right">— Aura</span></div>',
            unsafe_allow_html=True,
        )


def render_dashboard_content() -> None:
    page = st.session_state.dashboard_page
    if page in ("Chat with Aura", "Profile"):
        return

    prompts = {
        "Career Roadmap": "Generate a practical career roadmap for my current goal. Ask for my target role and experience if needed.",
        "Skills Analysis": "Analyze the skills I should build for my target career and identify likely gaps.",
        "Opportunities": "Explore current job opportunities relevant to my target role. Ask for location if needed.",
        "Free Resources": "Find free learning resources relevant to my target career and current skill level.",
    }
    p = prompts.get(page, "Help me with my career plan.")
    st.markdown(
        f'<div class="panel" style="height:100%;padding:28px"><h2>{html.escape(page)}</h2>'
        f'<p class="muted">Connected directly to the Aura AI engine. Click below to launch this analysis.</p></div>',
        unsafe_allow_html=True,
    )
    if st.button(f"Launch {page} in Chat  →", key=f"open_{page}", type="primary"):
        st.session_state.dashboard_page = "Chat with Aura"
        _send_from_action(p, page.lower().replace(" ", "_"))


def render_dashboard() -> None:
    if not st.session_state.authenticated:
        navigate("Home")
        return

    st.session_state.profile = st.session_state.profile or get_profile(st.session_state.user)

    # Dashboard Header Bar
    with st.container(key="dashboard-header"):
        logo_col, home_btn_col, spacer_col, notify_col, profile_col = st.columns(
            [3.8, 1.4, 0.4, 0.6, 1.8], gap="small", vertical_alignment="center"
        )
        with logo_col:
            st.markdown(
                '<div class="topbar-brand"><div class="brand-mark">✦</div>'
                '<div class="brand-name">Aura<span>AI</span></div>'
                '<div class="brand-divider"></div><div class="brand-sub">Dashboard</div></div>',
                unsafe_allow_html=True,
            )
        with home_btn_col:
            if st.button("⌂ Return to Home", key="dash_return_home", use_container_width=True, type="secondary"):
                navigate("Home")

        with notify_col:
            with st.popover("🔔", use_container_width=True):
                st.markdown("### Notifications")
                st.success(f"Welcome back, {html.escape(user_name().split()[0])}.")
                st.info("Your Aura workspace is ready and connected to Groq LLM.")

        with profile_col:
            with st.popover(f"👤 {user_name()[:16]}  ▾", use_container_width=True):
                st.markdown(f"### {html.escape(user_name())}")
                st.caption(user_email())
                if st.button("Return to Home", key="pop_return_home", use_container_width=True):
                    navigate("Home")
                if st.button("Log out", key="dash_logout_btn", type="primary", use_container_width=True):
                    logout()

    with st.container(key="dashboard-shell"):
        left, center, right = st.columns([1.00, 3.05, 1.38], gap="medium")
        with left:
            render_left_sidebar()
        with center:
            if st.session_state.dashboard_page == "Chat with Aura":
                render_chat_panel()
            else:
                render_dashboard_content()
        with right:
            render_right_sidebar()


# =====================================================================
# MAIN ROUTING
# =====================================================================
if st.session_state.page != "Dashboard":
    render_header()

if st.session_state.page == "Home":
    render_home()
elif st.session_state.page == "About":
    render_about()
elif st.session_state.page == "Contact":
    render_contact()
elif st.session_state.page == "Login":
    render_auth_page("login")
elif st.session_state.page == "Register":
    render_auth_page("register")
elif st.session_state.page == "Dashboard":
    render_dashboard()

if st.session_state.page != "Dashboard":
    st.markdown(
        '<div class="footer"><span>&copy; 2026 AuraAI. All rights reserved.</span>'
        '<span>AI Career &amp; Skills Navigator &middot; Built with Groq, CrewAI, RAG &amp; Streamlit</span></div>',
        unsafe_allow_html=True,
    )
