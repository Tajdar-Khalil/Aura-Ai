from __future__ import annotations

import base64
import hashlib
import html
from datetime import datetime
from pathlib import Path

import streamlit as st

from agent import run_aura
from firebase_service import firebase_available, login_user, register_user, send_login_notification
from memory import ConversationMemory
from rag import retrieve_context
from security import sanitize_output, validate_user_input
from services.profile_service import get_profile, mark_complete, save_recent_chat, set_goal
from ui.styles import inject_styles

BASE_DIR = Path(__file__).resolve().parent
AVATAR = BASE_DIR / "assets" / "aura_avatar.jpg"

st.set_page_config(page_title="AuraAI — AI Career & Skills Navigator", page_icon="✦", layout="wide", initial_sidebar_state="collapsed")
inject_styles()

DEFAULTS = {
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
    auth_dialog()


@st.dialog("Welcome to Aura", width="small")
def auth_dialog():
    mode = st.session_state.get("auth_mode", "login")
    st.markdown("### ✦ AuraAI")
    st.caption("AI Career & Skills Navigator")
    login_tab, register_tab = st.columns(2)
    with login_tab:
        if st.button("Login", key="dialog_login_tab", use_container_width=True, type="primary" if mode == "login" else "secondary"):
            st.session_state.auth_mode = "login"
            st.rerun()
    with register_tab:
        if st.button("Register", key="dialog_register_tab", use_container_width=True, type="primary" if mode == "register" else "secondary"):
            st.session_state.auth_mode = "register"
            st.rerun()

    if not firebase_available():
        st.warning("Firebase authentication is not configured. Add the Firebase settings required by the original project to Streamlit Secrets before deploying.")

    with st.form("aura_auth_form", clear_on_submit=False):
        name = st.text_input("Full name", placeholder="Your full name") if mode == "register" else ""
        email = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input("Password", type="password", placeholder="Your password")
        confirm = st.text_input("Confirm password", type="password") if mode == "register" else ""
        fcm_token = st.text_input("FCM token (optional)", type="password") if mode == "register" else ""
        submitted = st.form_submit_button("Create account" if mode == "register" else "Log in", type="primary", use_container_width=True)

    if submitted:
        try:
            if not email or not password:
                raise ValueError("Email and password are required.")
            if mode == "register":
                if not name.strip():
                    raise ValueError("Full name is required.")
                if password != confirm:
                    raise ValueError("Passwords do not match.")
                if len(password) < 6:
                    raise ValueError("Firebase requires a password of at least 6 characters.")
                result = register_user(name, email, password, fcm_token)
            else:
                result = login_user(email, password)

            st.session_state.authenticated = True
            st.session_state.user = result
            st.session_state.profile = get_profile(result)
            st.session_state.page = "Dashboard"
            st.session_state.dashboard_page = "Chat with Aura"
            st.session_state.auth_notice = ""
            if fcm_token and mode == "login":
                send_login_notification(fcm_token, result.get("name") or "Aura user")
            st.rerun()
        except Exception as exc:
            st.error(str(exc))


def render_header() -> None:
    st.markdown('<div class="topbar"><div class="brand"><div class="brand-mark">✦</div><div class="brand-name">Aura<span>AI</span></div><div class="brand-divider"></div><div class="brand-sub">AI Career &amp; Skills Navigator</div></div></div>', unsafe_allow_html=True)
    cols = st.columns([1, 1, 1, 1.25, 1.2, 1.2])
    for i, label in enumerate(["Home", "About", "Contact"]):
        with cols[i]:
            if st.button(label, key=f"public_{label}", use_container_width=True, type="primary" if st.session_state.page == label else "secondary"):
                navigate(label)
    with cols[3]:
        if st.session_state.authenticated:
            if st.button("Dashboard", key="public_dashboard", use_container_width=True, type="primary"):
                navigate("Dashboard")
        else:
            if st.button("Login", key="public_login", use_container_width=True):
                open_auth("login")
    with cols[4]:
        if not st.session_state.authenticated:
            if st.button("Register", key="public_register", use_container_width=True, type="primary"):
                open_auth("register")
    with cols[5]:
        if st.session_state.authenticated:
            if st.button(f"{initials(user_name())}  {user_name()[:16]}", key="public_logout", use_container_width=True):
                logout()


def render_home() -> None:
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    left, right = st.columns([1.08, .92], gap="large")
    with left:
        st.markdown('<span class="eyebrow">✦ &nbsp; Your AI Career Coach</span>', unsafe_allow_html=True)
        st.markdown('<h1>Navigate your next move with <span class="gradient">clarity.</span></h1>', unsafe_allow_html=True)
        st.markdown('<div class="hero-copy">AI Career &amp; Skills Navigator helps you identify skill gaps, find free learning resources, and explore real-time job market trends — all in one place.</div>', unsafe_allow_html=True)
        st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
        if st.button("💬  Explore Aura AI  →", key="explore_aura", use_container_width=False, type="primary"):
            if st.session_state.authenticated:
                navigate("Dashboard")
            else:
                open_auth("login")
        st.markdown('</div>', unsafe_allow_html=True)
    with right:
        st.markdown(f'<div class="aura-stage"><img src="{aura_data_uri()}"/><div class="aura-bubble"><b>✦ &nbsp; Hi, I\'m Aura!</b><span>Your AI Career &amp; Skills Navigator</span></div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('''<div class="feature-grid"><div class="feature"><div class="feature-icon">◎</div><h3>Find Skill Gaps</h3><p>Discover what skills to build next.</p></div><div class="feature"><div class="feature-icon">▣</div><h3>Learn for Free</h3><p>Get curated free resources &amp; courses.</p></div><div class="feature"><div class="feature-icon">↗</div><h3>Market Trends</h3><p>Explore real-time job opportunities.</p></div><div class="feature"><div class="feature-icon">◈</div><h3>Build Your Future</h3><p>Get personalized career guidance.</p></div></div>''', unsafe_allow_html=True)


def render_about() -> None:
    st.markdown('<div class="section"><h2>About AuraAI</h2><p class="muted">Aura is an AI career coach that understands a user goal, retrieves relevant knowledge, uses approved tools when needed, and keeps the user in control of consequential decisions.</p></div>', unsafe_allow_html=True)
    st.markdown('''<div class="cards"><div class="glass"><h3>Agentic workflow</h3><p>Goal → Decide → Act → Observe → Continue/Complete. CrewAI orchestrates the agent, while the existing project policy limits execution retries.</p></div><div class="glass"><h3>RAG knowledge base</h3><p>FAISS and the all-MiniLM-L6-v2 embedding model retrieve project-specific career information before the LLM answers.</p></div><div class="glass"><h3>Human-in-the-loop</h3><p>Important career decisions can pause for explicit approval, rejection, or a revised request.</p></div></div>''', unsafe_allow_html=True)


def render_contact() -> None:
    st.markdown('<div class="section"><h2>Contact AuraAI</h2><p class="muted">Questions, feedback, or ideas for Aura? Use the contact details below.</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="glass"><b>Email</b><br><span class="muted">daniyalriazcute@gmail.com</span><br><br><b>Project</b><br><span class="muted">AuraAI — AI Career &amp; Skills Navigator</span></div>', unsafe_allow_html=True)


def _safe_markdown(text: str) -> str:
    return html.escape(sanitize_output(text)).replace("\n", "<br>")


def _format_time(value: str | None = None) -> str:
    return value or datetime.now().strftime("%I:%M %p")


def _dashboard_intro() -> str:
    name = html.escape(user_name().split()[0])
    return (f"Great question, <b>{name}</b>! Becoming a stronger career professional requires a mix of technical skills, hands-on practice, and continuous learning. "
            "Aura can use your goal, recent conversation, project knowledge base and approved tools to build a practical plan.")


def _seed_messages() -> list[dict]:
    return []


def _add_user_message(prompt: str) -> None:
    prompt = validate_user_input(prompt)
    if not prompt:
        return
    st.session_state.messages.append({"role": "user", "content": prompt, "time": _format_time()})
    st.session_state.profile = mark_complete(st.session_state.user, "chat")
    title = prompt if len(prompt) <= 80 else prompt[:77] + "..."
    st.session_state.profile = save_recent_chat(st.session_state.user, title, prompt)
    decision = requires_approval(prompt)
    if decision["required"]:
        st.session_state.pending_approval = {"query": prompt, **decision}
        return
    _run_and_store(prompt, approved=False)


def _run_and_store(prompt: str, approved: bool) -> None:
    with st.spinner("Aura is working through your request..."):
        try:
            retrieved = retrieve_context(prompt, k=4)
            result = run_aura(user_query=prompt, memory=st.session_state.memory, retrieved_context=retrieved, human_approved=approved)
            safe = sanitize_output(result)
            st.session_state.memory.add("user", prompt)
            st.session_state.memory.add("assistant", safe)
            st.session_state.messages.append({"role": "assistant", "content": safe, "time": _format_time()})
        except Exception as exc:
            st.session_state.messages.append({"role": "assistant", "content": f"I couldn't complete that request. Please try again. Technical detail: {sanitize_output(exc)}", "time": _format_time()})


def requires_approval(prompt: str) -> dict:
    text = prompt.lower().strip()
    consequential = ["should i quit", "should i resign", "should i leave my job", "should i accept", "should i reject", "which career should i choose", "which career should i pursue", "choose a career for me", "should i switch careers", "should i change careers", "should i spend", "should i pay", "should i relocate", "should i move", "make the decision for me"]
    preference_sensitive = ["based on my situation", "based on my experience", "personalized recommendation", "what should i do", "what would you choose for me", "recommend one for me", "which one is right for me"]
    if any(p in text for p in consequential):
        return {"required": True, "reason": "This request asks Aura to support a consequential personal career decision.", "action": "Review relevant options, trade-offs and evidence before Aura provides a personalized recommendation."}
    if any(p in text for p in preference_sensitive):
        return {"required": True, "reason": "This request depends on an important personal preference or situation.", "action": "Use conversation context to prepare a personalized comparison and practical next step."}
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
    if completion_key:
        st.session_state.profile = mark_complete(st.session_state.user, completion_key)
    _add_user_message(prompt)
    st.rerun()


def render_chat_panel() -> None:
    st.markdown('<div class="panel chat-panel"><div class="chat-head"><div class="chat-title"><span class="spark">✦</span><div><b>Chat with Aura</b><div class="muted">Your AI Career Coach</div></div></div><span class="online">● &nbsp; Aura is online</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="msg-area">', unsafe_allow_html=True)
    if not st.session_state.messages:
        st.markdown(f'<div class="bubble me">What should I learn to reach my career goal?<small>{_format_time()} ✓✓</small></div><div class="bubble assistant"><b style="color:#4db3ff">✦ Aura</b><br>{_dashboard_intro()}<div class="section-box"><h5>How Aura can help</h5><ul><li>Identify skill gaps and foundations</li><li>Create a career roadmap</li><li>Find learning resources</li><li>Research current opportunities when needed</li></ul></div><span class="muted">Start by telling Aura your target role and current experience.</span></div>', unsafe_allow_html=True)
    for message in st.session_state.messages:
        _render_message(message)
    pending = st.session_state.pending_approval
    st.markdown('</div>', unsafe_allow_html=True)
    if pending:
        st.warning(f"Human approval required\n\n{pending['reason']}\n\nRequested action: {pending['action']}")
        a, b = st.columns(2)
        with a:
            if st.button("✓ Approve and continue", key="approve", type="primary", use_container_width=True):
                query = pending["query"]
                st.session_state.pending_approval = None
                _run_and_store(query, approved=True)
                st.rerun()
        with b:
            if st.button("✕ Reject / revise", key="reject", use_container_width=True):
                st.session_state.pending_approval = None
                st.session_state.messages.append({"role":"assistant","content":"No problem. I will not proceed with that action. Tell me how you would like to adjust the request.","time":_format_time()})
                st.rerun()
    chip_cols = st.columns(4)
    chips = [("Show me a 90-day roadmap", "roadmap"), ("Free learning resources", "resources"), ("Compare AppSec vs GRC", "skills"), ("Help me with job applications", "opportunities")]
    for col, (label, key) in zip(chip_cols, chips):
        with col:
            if st.button(label, key=f"chip_{key}", use_container_width=True):
                _send_from_action(label, key)
    with st.form("chat_form", clear_on_submit=True):
        cols = st.columns([.08, .84, .08])
        with cols[0]:
            st.markdown("📎")
        with cols[1]:
            prompt = st.text_input("Message", placeholder="Type your message to Aura...", label_visibility="collapsed")
        with cols[2]:
            send = st.form_submit_button("➤", use_container_width=True, type="primary")
    st.markdown('</div>', unsafe_allow_html=True)
    if send and prompt:
        _add_user_message(prompt)
        st.rerun()


def render_left_sidebar() -> None:
    profile = st.session_state.profile or get_profile(st.session_state.user)
    st.session_state.profile = profile
    items = [
        ("Chat with Aura", "chat"), ("Career Roadmap", "roadmap"), ("Skills", "skills"), ("Opportunities", "opportunities"), ("Resources", "resources")
    ]
    st.markdown('<div class="side">', unsafe_allow_html=True)
    for label, key in items:
        cls = "selected" if st.session_state.dashboard_page == label else ""
        st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)
        if st.button(label, key=f"side_{key}", use_container_width=True):
            st.session_state.dashboard_page = label
            if label != "Chat with Aura":
                st.session_state.profile = mark_complete(st.session_state.user, key)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    progress = int(profile.get("progress", 0))
    st.markdown(f'<div class="panel progress-card"><b>Your Progress</b><div class="progress-row" style="margin-top:12px"><div class="ring" style="--p:{progress}"><div>{progress}%</div></div><div><div>Career Growth</div><div class="muted">Journey</div></div></div></div>', unsafe_allow_html=True)
    st.markdown('<div class="panel recent"><b>Recent Chats</b>', unsafe_allow_html=True)
    chats = profile.get("recent_chats") or []
    if not chats:
        st.markdown('<p class="muted" style="margin-top:12px">No conversations yet.</p>', unsafe_allow_html=True)
    for item in chats[:4]:
        st.markdown(f'<div class="chat-row"><b>{html.escape(item.get("title", "Conversation"))}</b><small>{html.escape(item.get("timestamp", ""))}</small></div>', unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)


def render_right_sidebar() -> None:
    email = user_email()
    img = avatar_url(email)
    st.markdown('<div class="right-panel">', unsafe_allow_html=True)
    st.markdown(f'<div class="panel aura-card"><div class="aura-pic"><img src="{aura_data_uri()}"/></div><h2>Aura <span>AI</span></h2><div>Your Career Coach &amp; Guide</div><p class="muted">Smart guidance. Better decisions. A brighter future.</p></div>', unsafe_allow_html=True)
    facts = [("◉", "Powered by GPT-OSS-120B", "Advanced reasoning & analysis"), ("▣", "RAG Knowledge Base", "Curated career resources"), ("♣", "4 External Tools", "Search · Wikipedia · API · Calculator"), ("◌", "Human-in-the-Loop", "For important decisions & preferences")]
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    for icon, title, sub in facts:
        st.markdown(f'<div class="fact"><div class="fact-icon">{icon}</div><div><b>{title}</b><small>{sub}</small></div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel quick"><h4>⚡ Quick Actions</h4>', unsafe_allow_html=True)
    actions = [("Generate Career Roadmap", "Generate my career roadmap", "roadmap"), ("Analyze My Skills", "Analyze my skills", "skills"), ("Explore Job Opportunities", "Explore job opportunities", "opportunities"), ("Find Learning Resources", "Find free learning resources", "resources")]
    for label, prompt, key in actions:
        if st.button(label + "  ›", key=f"quick_{key}", use_container_width=True):
            st.session_state.dashboard_page = "Chat with Aura"
            _send_from_action(prompt, key)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="quote">✦ &nbsp; “Big dreams need a plan.<br>&nbsp;&nbsp;&nbsp;&nbsp;I\'m here to help you build yours.”<br><span style="float:right">— Aura</span></div></div>', unsafe_allow_html=True)


def render_dashboard_content() -> None:
    page = st.session_state.dashboard_page
    if page == "Chat with Aura":
        return
    prompts = {
        "Career Roadmap": "Generate a practical career roadmap for my current goal. Ask for my target role and experience if needed.",
        "Skills": "Analyze the skills I should build for my target career and identify likely gaps.",
        "Opportunities": "Explore current job opportunities relevant to my target role. Ask for location if needed.",
        "Resources": "Find free learning resources relevant to my target career and current skill level.",
    }
    st.markdown(f'<div class="panel" style="height:100%;padding:28px"><h2>{html.escape(page)}</h2><p class="muted">This section is connected to Aura. Use the action below to send the request through the same RAG + CrewAI workflow.</p></div>', unsafe_allow_html=True)
    if st.button(f"Open {page} in Chat", key=f"open_{page}", type="primary"):
        st.session_state.dashboard_page = "Chat with Aura"
        _send_from_action(prompts[page], page.lower().split()[0])


def render_dashboard() -> None:
    if not st.session_state.authenticated:
        navigate("Home")
        return
    st.session_state.profile = st.session_state.profile or get_profile(st.session_state.user)
    st.markdown(f'<div class="topbar"><div class="brand"><div class="brand-mark">✦</div><div class="brand-name">Aura<span>AI</span></div><div class="brand-divider"></div><div class="brand-sub">AI Career &amp; Skills Navigator</div></div><div class="profile-pill"><img src="{avatar_url(user_email())}"/><span>{html.escape(user_name())}</span><span>⌄</span></div></div>', unsafe_allow_html=True)
    left, center, right = st.columns([.95, 2.8, 1.2], gap="medium")
    with left:
        render_left_sidebar()
    with center:
        if st.session_state.dashboard_page == "Chat with Aura":
            render_chat_panel()
        else:
            render_dashboard_content()
    with right:
        render_right_sidebar()


# Public page header only. Dashboard gets the exact dashboard header inside its own layout.
if st.session_state.page != "Dashboard":
    render_header()

if st.session_state.page == "Home":
    render_home()
elif st.session_state.page == "About":
    render_about()
elif st.session_state.page == "Contact":
    render_contact()
elif st.session_state.page == "Dashboard":
    render_dashboard()

st.markdown('<div class="footer"><span>© 2026 AuraAI. All rights reserved.</span><span>AI Career &amp; Skills Navigator · Built with CrewAI, Groq, RAG &amp; Firebase</span></div>', unsafe_allow_html=True)
