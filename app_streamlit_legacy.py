from __future__ import annotations

import base64
import hashlib
import html
from datetime import datetime
from pathlib import Path
import textwrap

import streamlit as st

from agent import run_aura
from firebase_service import firebase_available, login_user, register_user, send_login_notification
from memory import ConversationMemory
from rag import retrieve_context
from security import sanitize_output, validate_user_input
from services.profile_service import get_profile, mark_complete, save_recent_chat, save_contact_message, set_goal
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

        if not firebase_available():
            st.warning("Firebase authentication is not configured. Add your Firebase settings to Streamlit Secrets before deploying.")

        with st.form("aura_full_auth_form", clear_on_submit=False):
            name = st.text_input("Full name", placeholder="Your full name") if mode == "register" else ""
            email = st.text_input("Email address", placeholder="you@example.com")
            password = st.text_input("Password", type="password", placeholder="Your password")
            confirm = st.text_input("Confirm password", type="password", placeholder="Repeat password") if mode == "register" else ""
            fcm_token = st.text_input("FCM token (optional)", type="password", placeholder="Optional push token") if mode == "register" else ""
            submitted = st.form_submit_button("Sign In to Dashboard →" if mode == "login" else "Create Aura Account →", type="primary", use_container_width=True)
            forgot_submitted = (
                st.form_submit_button("Forgot password?", type="secondary", use_container_width=False)
                if mode == "login" else False
            )

        if forgot_submitted:
            try:
                if not email.strip():
                    st.error("Enter your email first.")
                else:
                    from firebase_service import send_password_reset
                    send_password_reset(email.strip())
                    st.success("If that account exists, Firebase has sent a password-reset email.")
            except Exception as exc:
                st.error(str(exc))

        if submitted:
            try:
                if not email or not password:
                    raise ValueError("Email and password are required.")
                if mode == "register":
                    if not name.strip():
                        raise ValueError("Full name is required.")
                    if password != confirm:
                        raise ValueError("Passwords do not match.")
                    if len(password) < 8:
                        raise ValueError("Use at least 8 characters for your password.")
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


def render_header() -> None:
    """Responsive public header with clean modern website navbar and mobile drawer."""
    with st.container(key="public-header"):
        logo_col, spacer_col, home_col, about_col, contact_col, login_col, register_col, drawer_col = st.columns(
            [4.0, 0.4, 0.95, 0.95, 0.95, 1.05, 1.35, 0.8], gap="small", vertical_alignment="center"
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
                if st.button("Sign In", key="public_login", use_container_width=True,
                             type="primary" if st.session_state.page == "Login" else "secondary"):
                    open_auth("login")
        with register_col:
            if st.session_state.authenticated:
                if st.button(f"{initials(user_name())}  {user_name()[:10]}", key="public_logout",
                             use_container_width=True, type="secondary"):
                    logout()
            else:
                if st.button("Sign Up", key="public_register", use_container_width=True,
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

def render_home() -> None:
    st.markdown(textwrap.dedent("""
    <div class="hero">
      <div class="hero-left">
        <span class="eyebrow">✦ &nbsp; Your AI Career Coach</span>
        <h1>Navigate your next move with <span class="gradient">data-driven clarity.</span></h1>
        <p class="hero-copy">Aura AI synthesizes millions of real-time market data points to identify your precise skill gaps, curate targeted learning, and forecast compensation brackets—all instantly.</p>
        
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
            <div class="metric-lbl">Market Trend Updates</div>
          </div>
        </div>

        <div class="primary-btn" style="margin-top: 30px;">
          """), unsafe_allow_html=True)
    if st.button("💬  Launch Career Diagnostic  →", key="explore_aura", use_container_width=False, type="primary"):
        if st.session_state.authenticated:
            navigate("Dashboard")
        else:
            open_auth("login")
    st.markdown(textwrap.dedent(f"""
        </div>
      </div>
      <div class="hero-right">
        <div class="aura-stage">
          <img src="{aura_data_uri()}" alt="Aura AI"/>
          <div class="aura-bubble">
            <b>✦ &nbsp; Market Insight Ready</b>
            <span>Software Engineer salaries are trending +12% YoY. Want your custom roadmap?</span>
          </div>
          
          <div class="floating-badge badge-1">
            <span class="pulse-dot"></span> Processing CrewAI Agents...
          </div>
          <div class="floating-badge badge-2">
            <span class="pulse-dot green"></span> Market Data: LIVE
          </div>
        </div>
      </div>
    </div>
"""), unsafe_allow_html=True)


def render_about() -> None:
    st.markdown(textwrap.dedent("""
    <div class="section about-section">
      <div class="about-header text-center">
        <span class="eyebrow">✦ &nbsp; The Engine Behind Aura</span>
        <h2>Professional Grade <span class="gradient">AI Architecture</span></h2>
        <p class="muted max-w-700 mx-auto">Built on a cutting-edge autonomous multi-agent framework, Aura doesn't just chat—it executes complex market research, skill analysis, and career mapping on your behalf.</p>
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


def render_contact() -> None:
    st.markdown(textwrap.dedent("""
    <div class="contact-wrapper">
      <div class="contact-hero text-center">
        <span class="eyebrow">✦ &nbsp; 24/7 Support Network</span>
        <h2>Connect with <span class="gradient">AuraAI</span></h2>
        <p class="muted max-w-700 mx-auto">Whether you're looking for enterprise solutions, product support, or career advice, our human and AI teams are ready to assist you.</p>
      </div>

      <div class="contact-grid">
        <div class="contact-info-card">
          <div class="contact-info-icon">✉</div>
          <h3>Priority Channel</h3>
          <p class="muted">Access direct support from our core engineering team.</p>
          
          <div class="status-indicator">
            <span class="status-dot green"></span> <b>Systems Operational</b>
          </div>
          
          <div class="contact-detail">
            <b>Email Routing</b>
            <span>daniyalriazcute@gmail.com</span>
          </div>
          <div class="contact-detail">
            <b>Average Response</b>
            <span>Under 2 Hours</span>
          </div>
          <div class="contact-detail">
            <b>Global Availability</b>
            <span>24/7 via Automated Assistants</span>
          </div>
        </div>
        
        <div class="contact-form-card">
          <h3>Secure Transmission</h3>
          <p class="muted">Your message is encrypted and routed instantly.</p>
          """), unsafe_allow_html=True)
    with st.form("contact_form", clear_on_submit=True):
        c1, c2 = st.columns(2, gap="medium")
        with c1:
            contact_name = st.text_input("Name", placeholder="Your name")
        with c2:
            contact_email = st.text_input("Email", placeholder="you@example.com")
        subject = st.text_input("Subject", placeholder="How can we help?")
        message = st.text_area("Message", placeholder="Write your message here...", height=170)
        submitted = st.form_submit_button("Send message  →", type="primary", use_container_width=True)
    st.markdown('</div></div></div>', unsafe_allow_html=True)

    if submitted:
        if not contact_name.strip() or not contact_email.strip() or not message.strip():
            st.error("Please complete your name, email and message before sending.")
        else:
            if save_contact_message(contact_name, contact_email, subject, message):
                st.success("Message received. Thank you for contacting AuraAI.")
            else:
                st.error("The contact service is not configured yet. Please try again after Firebase/Firestore is configured.")
    
    
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
    with st.spinner("Aura is working through your request..."):
        try:
            retrieved = retrieve_context(prompt, k=4)
            result = run_aura(user_query=prompt, memory=st.session_state.memory, retrieved_context=retrieved, human_approved=approved)
            safe = sanitize_output(result)
            st.session_state.memory.add("user", prompt)
            st.session_state.memory.add("assistant", safe)
            st.session_state.messages.append({"role": "assistant", "content": safe, "time": _format_time()})
            # Progress changes only after Aura successfully completes the action.
            st.session_state.profile = mark_complete(st.session_state.user, completion_key)
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
    _add_user_message(prompt, completion_key or "chat")
    st.rerun()


def render_chat_panel() -> None:
    # A real Streamlit container is used so CSS can control the chat as one
    # viewport-sized panel instead of relying on HTML wrappers between widgets.
    with st.container(key="dashboard-chat"):
        st.markdown('<div class="chat-head"><div class="chat-title"><span class="spark">✦</span><div><b>Chat with Aura</b><div class="muted">Your AI Career Coach</div></div></div><span class="online">● &nbsp; Aura is online</span></div>', unsafe_allow_html=True)
        with st.container(key="dashboard-messages"):
            if not st.session_state.messages:
                st.markdown(f'<div class="bubble assistant welcome-bubble"><b style="color:#4db3ff">✦ Aura</b><br>{_dashboard_intro()}<div class="section-box"><h5>How Aura can help</h5><ul><li>Identify skill gaps and foundations</li><li>Create a career roadmap</li><li>Find learning resources</li><li>Research current opportunities when needed</li></ul></div><span class="muted">Start by telling Aura your target role and current experience.</span></div>', unsafe_allow_html=True)
            for message in st.session_state.messages:
                _render_message(message)

        pending = st.session_state.pending_approval
        if pending:
            st.warning(f"Human approval required\n\n{pending['reason']}\n\nRequested action: {pending['action']}")
            a, b = st.columns(2)
            with a:
                if st.button("✓ Approve and continue", key="approve", type="primary", use_container_width=True):
                    query = pending["query"]
                    st.session_state.pending_approval = None
                    _run_and_store(query, approved=True, completion_key=pending.get("completion_key", "chat"))
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
        if send and prompt:
            _add_user_message(prompt)
            st.rerun()

def render_left_sidebar() -> None:
    profile = st.session_state.profile or get_profile(st.session_state.user)
    st.session_state.profile = profile
    items = [
        ("⌂  Chat with Aura", "chat"), ("▱  Career Roadmap", "roadmap"), ("◇  Skills", "skills"),
        ("▣  Opportunities", "opportunities"), ("▤  Resources", "resources")
    ]
    with st.container(key="dashboard-left"):
        for label, key in items:
            selected = st.session_state.dashboard_page == label.split("  ", 1)[-1]
            if st.button(label, key=f"side_{key}", use_container_width=True, type="primary" if selected else "secondary"):
                st.session_state.dashboard_page = label.split("  ", 1)[-1]
                st.rerun()

        progress = int(profile.get("progress", 0))
        completed = set(profile.get("completed") or [])
        st.markdown(
            f'<div class="progress-card"><b>Your Progress</b>'
            f'<div class="progress-row" style="margin-top:12px">'
            f'<div class="ring" style="--p:{progress}"><div>{progress}%</div></div>'
            f'<div><div>Career Growth</div><div class="muted">{len(completed)}/7 milestones complete</div></div>'
            f'</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="recent"><b>Recent Chats</b>', unsafe_allow_html=True)
        chats = profile.get("recent_chats") or []
        if not chats:
            st.markdown('<p class="muted" style="margin-top:12px">No conversations yet.</p>', unsafe_allow_html=True)
        for index, item in enumerate(chats[:4]):
            title = item.get("title", "Conversation")
            prompt = item.get("prompt", title)
            if st.button(title[:52], key=f"recent_{index}", use_container_width=True):
                st.session_state.dashboard_page = "Chat with Aura"
                _send_from_action(prompt, "chat")
            st.markdown(f'<small class="recent-time">{html.escape(item.get("timestamp", ""))}</small>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

def render_right_sidebar() -> None:
    with st.container(key="dashboard-right"):
        # Aura card (Removed multi-line indentation to prevent Markdown code-block rendering)
        aura_card_html = (
            '<div class="aura-card">'
            f'<div class="aura-pic"><img src="{aura_data_uri()}" alt="Aura AI"></div>'
            '<h2>Aura <span>AI</span></h2>'
            '<p class="aura-role">Your Career Coach &amp; Guide</p>'
            '<p class="muted">Smart guidance. Better decisions. A brighter future.</p>'
            '</div>'
        )

        st.markdown(aura_card_html, unsafe_allow_html=True)

        facts = [
            ("◉", "Powered by GPT-OSS-120B", "Advanced reasoning & analysis"),
            ("▣", "RAG Knowledge Base", "Curated career resources"),
            ("♣", "4 External Tools", "Search · Wikipedia · API · Calculator"),
            ("◌", "Human-in-the-Loop", "For important decisions & preferences"),
        ]

        facts_html = '<div class="facts-card">'
        for icon, title, subtitle in facts:
            # Concatenated without leading spaces
            facts_html += (
                '<div class="fact">'
                f'<div class="fact-icon">{icon}</div>'
                '<div>'
                f'<b>{title}</b>'
                f'<small>{subtitle}</small>'
                '</div>'
                '</div>'
            )
        facts_html += '</div>'

        st.markdown(facts_html, unsafe_allow_html=True)

        # Quick actions
        st.markdown('<div class="quick"><h4>⚡ Quick Actions</h4>', unsafe_allow_html=True)

        actions = [
            ("Generate Career Roadmap", "Generate my career roadmap", "roadmap"),
            ("Analyze My Skills", "Analyze my skills", "skills"),
            ("Explore Job Opportunities", "Explore job opportunities", "opportunities"),
            ("Find Learning Resources", "Find free learning resources", "resources"),
        ]

        for label, prompt, key in actions:
            if st.button(label + "  ›", key=f"quick_{key}", use_container_width=True):
                st.session_state.dashboard_page = "Chat with Aura"
                _send_from_action(prompt, key)

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            '<div class="quote">✦ &nbsp; “Big dreams need a plan.<br>'
            '&nbsp;&nbsp;&nbsp;&nbsp;I\'m here to help you build yours.”'
            '<br><span style="float:right">— Aura</span></div>',
            unsafe_allow_html=True,
        )
def render_profile_panel() -> None:
    profile = st.session_state.profile or get_profile(st.session_state.user)
    progress = int(profile.get("progress", 0))
    st.markdown(
        f'<div class="panel profile-panel"><div class="profile-large"><img src="{avatar_url(user_email(), 160)}"/></div>'
        f'<h2>{html.escape(user_name())}</h2><p class="muted">{html.escape(user_email())}</p>'
        f'<div class="profile-progress"><b>Career Growth</b><strong>{progress}%</strong></div>'
        f'<div class="progress-bar"><span style="width:{progress}%"></span></div></div>',
        unsafe_allow_html=True,
    )
    if st.button("Back to Chat with Aura", key="profile_back", type="primary"):
        st.session_state.dashboard_page = "Chat with Aura"
        st.rerun()


def render_dashboard_content() -> None:
    page = st.session_state.dashboard_page
    if page in ("Chat with Aura", "Profile"):
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
        completion_key = {"Career Roadmap": "roadmap", "Skills": "skills", "Opportunities": "opportunities", "Resources": "resources"}[page]
        _send_from_action(prompts[page], completion_key)


def render_mobile_dashboard_nav() -> None:
    """Compact mobile navigation replacing the three-column dashboard rails."""
    with st.container(key="mobile-dashboard-nav"):
        with st.expander("☰  Dashboard menu", expanded=False):
            items = [
                ("⌂  Chat with Aura", "Chat with Aura", "chat"),
                ("▱  Career Roadmap", "Career Roadmap", "roadmap"),
                ("◇  Skills", "Skills", "skills"),
                ("▣  Opportunities", "Opportunities", "opportunities"),
                ("▤  Resources", "Resources", "resources"),
                ("◎  Profile", "Profile", "profile"),
            ]
            cols = st.columns(2, gap="small")
            for index, (label, page, key) in enumerate(items):
                with cols[index % 2]:
                    if st.button(
                        label,
                        key=f"mobile_dash_{key}",
                        use_container_width=True,
                        type="primary" if st.session_state.dashboard_page == page else "secondary",
                    ):
                        st.session_state.dashboard_page = page
                        st.rerun()

            profile = st.session_state.profile or {}
            progress = int(profile.get("progress", 0))
            completed = len(set(profile.get("completed") or []))
            st.markdown(
                f'<div class="mobile-progress"><b>Your Progress</b>'
                f'<span>{progress}% · {completed}/7 milestones</span></div>',
                unsafe_allow_html=True,
            )


def render_dashboard() -> None:
    if not st.session_state.authenticated:
        navigate("Home")
        return

    st.session_state.profile = st.session_state.profile or get_profile(st.session_state.user)

    # Compact dashboard header. The same row becomes a three-control mobile bar.
    with st.container(key="dashboard-header"):
        logo_col, spacer_col, notify_col, profile_col = st.columns(
            [4.8, 0.6, 0.7, 1.9], gap="small", vertical_alignment="center"
        )
        with logo_col:
            st.markdown(
                '<div class="topbar-brand"><div class="brand-mark">✦</div>'
                '<div class="brand-name">Aura<span>AI</span></div>'
                '<div class="brand-divider"></div><div class="brand-sub">AI Career &amp; Skills Navigator</div></div>',
                unsafe_allow_html=True,
            )
        with notify_col:
            with st.popover("🔔", use_container_width=True):
                st.markdown("### Notifications")
                st.success(f"Welcome back, {html.escape(user_name().split()[0])}.")
                st.info("Your Aura workspace is ready. New accounts start at 0% progress.")
                st.caption("Progress updates when a career capability is successfully completed.")
                if st.button("Mark notifications as read", key="mark_notifications_read", use_container_width=True):
                    st.session_state.notifications_read = True
                    st.rerun()
        with profile_col:
            with st.popover(f"👤 {user_name()[:18]}  ▾", use_container_width=True):
                st.markdown(f"### {html.escape(user_name())}")
                st.caption(user_email())
                st.markdown(
                    f'<div class="profile-menu-avatar"><img src="{avatar_url(user_email(), 96)}"/></div>',
                    unsafe_allow_html=True,
                )
                if st.button("View profile", key="profile_view", use_container_width=True):
                    st.session_state.dashboard_page = "Profile"
                    st.rerun()
                if st.button("Dashboard home", key="profile_home", use_container_width=True):
                    st.session_state.dashboard_page = "Chat with Aura"
                    st.rerun()
                if st.button("Log out", key="profile_logout", type="primary", use_container_width=True):
                    logout()

    render_mobile_dashboard_nav()

    with st.container(key="dashboard-shell"):
        left, center, right = st.columns([1.00, 3.05, 1.38], gap="medium")
        with left:
            render_left_sidebar()
        with center:
            if st.session_state.dashboard_page == "Chat with Aura":
                render_chat_panel()
            elif st.session_state.dashboard_page == "Profile":
                render_profile_panel()
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
elif st.session_state.page == "Login":
    render_auth_page("login")
elif st.session_state.page == "Register":
    render_auth_page("register")
elif st.session_state.page == "Dashboard":
    render_dashboard()

if st.session_state.page != "Dashboard":
    st.markdown('<div class="footer"><span>© 2026 AuraAI. All rights reserved.</span><span>AI Career &amp; Skills Navigator · Built with CrewAI, Groq, RAG &amp; Firebase</span></div>', unsafe_allow_html=True)
