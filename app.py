from __future__ import annotations

import os
import re
import base64
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from memory import ConversationMemory
from rag import retrieve_context
from agent import run_aura


# ============================================================
# BASIC CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

st.set_page_config(
    page_title="AuraAI | AI Career & Skills Navigator",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# GROQ KEY
# ============================================================

def get_groq_key() -> str:

    key = os.getenv("GROQ_API_KEY", "").strip()

    if key.startswith("gsk_"):
        return key

    try:

        if "GROQ_API_KEY" in st.secrets:

            key = str(
                st.secrets["GROQ_API_KEY"]
            ).strip()

            if key.startswith("gsk_"):
                return key

    except Exception:
        pass

    return ""


# ============================================================
# SESSION MEMORY
# ============================================================

if "aura_memory" not in st.session_state:

    st.session_state.aura_memory = ConversationMemory(
        max_turns=8
    )


if "messages" not in st.session_state:

    st.session_state.messages = []


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>

/* =========================================================
   STREAMLIT RESET
   ========================================================= */

#MainMenu {
    visibility: hidden;
}

header {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

[data-testid="stToolbar"] {
    visibility: hidden;
}

[data-testid="stDecoration"] {
    visibility: hidden;
}

[data-testid="stStatusWidget"] {
    visibility: hidden;
}

html,
body,
.stApp {

    background:
        radial-gradient(
            circle at 10% 10%,
            rgba(37,140,255,0.10),
            transparent 35%
        ),
        #030a1f !important;

    color: #f2f6ff !important;
}


/* =========================================================
   MAIN CONTAINER
   ========================================================= */

.block-container {

    max-width: 1250px !important;

    padding-top: 1rem !important;
    padding-bottom: 7rem !important;

}


/* =========================================================
   AURA HEADER
   ========================================================= */

.aura-header {

    position: sticky;

    top: 0;

    z-index: 999;

    display: flex;

    align-items: center;

    justify-content: space-between;

    padding: 16px 22px;

    margin-bottom: 22px;

    border:

        1px solid
        rgba(96,165,250,0.18);

    border-radius: 18px;

    background:

        rgba(3,10,31,0.88);

    backdrop-filter: blur(20px);

    box-shadow:

        0 15px 50px
        rgba(0,0,0,0.25);

}


.aura-brand {

    display: flex;

    align-items: center;

    gap: 12px;

}


.aura-logo {

    width: 42px;

    height: 42px;

    display: flex;

    align-items: center;

    justify-content: center;

    border-radius: 13px;

    background:

        linear-gradient(
            135deg,
            #258cff,
            #7c3aed
        );

    color: white;

    font-size: 21px;

    font-weight: 800;

    box-shadow:

        0 8px 25px
        rgba(37,140,255,0.30);

}


.aura-title {

    font-size: 1.05rem;

    font-weight: 800;

    color: #ffffff;

}


.aura-subtitle {

    font-size: 0.72rem;

    color: #8fa7ce;

    margin-top: 2px;

}


.ai-status {

    display: flex;

    align-items: center;

    gap: 8px;

    padding: 8px 12px;

    border-radius: 999px;

    border:

        1px solid
        rgba(34,197,94,0.25);

    background:

        rgba(34,197,94,0.08);

    color: #86efac;

    font-size: 0.75rem;

}


.status-dot {

    width: 7px;

    height: 7px;

    border-radius: 50%;

    background: #22c55e;

    box-shadow:

        0 0 10px
        rgba(34,197,94,0.8);

}


/* =========================================================
   HERO
   ========================================================= */

.aura-hero {

    text-align: center;

    padding: 35px 20px 22px;

}


.aura-hero h1 {

    margin: 0;

    font-size: clamp(
        2rem,
        5vw,
        3.5rem
    );

    line-height: 1.1;

    font-weight: 800;

    background:

        linear-gradient(
            135deg,
            #ffffff,
            #7dd3fc,
            #60a5fa
        );

    -webkit-background-clip: text;

    -webkit-text-fill-color: transparent;

}


.aura-hero p {

    max-width: 700px;

    margin: 15px auto 0;

    color: #91a7cb;

    line-height: 1.7;

}


/* =========================================================
   QUICK PROMPTS
   ========================================================= */

.quick-title {

    margin:

        12px 0 8px;

    color: #8fa7ce;

    font-size: 0.78rem;

    font-weight: 700;

}


div.stButton > button {

    border-radius: 12px !important;

    border:

        1px solid
        rgba(96,165,250,0.16) !important;

    background:

        rgba(15,32,65,0.70) !important;

    color: #dbeafe !important;

    transition: all .2s ease !important;

}


div.stButton > button:hover {

    border-color:

        rgba(96,165,250,0.45) !important;

    background:

        rgba(37,140,255,0.12) !important;

    transform: translateY(-1px);

}


/* =========================================================
   CHAT
   ========================================================= */

[data-testid="stChatMessage"] {

    border:

        1px solid
        rgba(96,165,250,0.10);

    border-radius: 18px;

    margin-bottom: 12px;

    padding: 4px;

}


[data-testid="stChatMessage"] p {

    line-height: 1.7;

}


[data-testid="stChatInput"] {

    border-radius: 18px !important;

}


/* =========================================================
   CARDS
   ========================================================= */

.aura-card {

    height: 100%;

    padding: 22px;

    border:

        1px solid
        rgba(96,165,250,0.13);

    border-radius: 18px;

    background:

        linear-gradient(
            145deg,
            rgba(15,32,65,0.78),
            rgba(7,18,42,0.72)
        );

}


.aura-card h3 {

    margin-top: 0;

    color: #ffffff;

}


.aura-card p {

    color: #91a7cb;

    line-height: 1.65;

}


.aura-card .icon {

    font-size: 1.8rem;

    margin-bottom: 10px;

}


/* =========================================================
   MOBILE
   ========================================================= */

@media(max-width: 700px) {

    .block-container {

        padding-left: 12px !important;

        padding-right: 12px !important;

    }

    .aura-header {

        padding: 12px 14px;

        border-radius: 14px;

    }

    .aura-subtitle {

        display: none;

    }

    .aura-hero {

        padding-top: 20px;

    }

    .aura-hero h1 {

        font-size: 2rem;

    }

}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# HEADER
# ============================================================

groq_key = get_groq_key()

if groq_key:

    status_html = """
    <div class="ai-status">
        <span class="status-dot"></span>
        Aura AI Live
    </div>
    """

else:

    status_html = """
    <div class="ai-status"
         style="
         border-color:rgba(245,158,11,.25);
         background:rgba(245,158,11,.08);
         color:#fde68a;">
        <span class="status-dot"
              style="
              background:#f59e0b;
              box-shadow:0 0 10px rgba(245,158,11,.7);">
        </span>
        AI Key Required
    </div>
    """


st.markdown(
    f"""
    <div class="aura-header">

        <div class="aura-brand">

            <div class="aura-logo">
                ✦
            </div>

            <div>

                <div class="aura-title">
                    AuraAI
                </div>

                <div class="aura-subtitle">
                    AI Career & Skills Navigator
                </div>

            </div>

        </div>

        {status_html}

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HERO
# ============================================================

st.markdown(
    """
    <div class="aura-hero">

        <h1>
            Your AI Career Navigator
        </h1>

        <p>
            Ask Aura about careers, skills, learning roadmaps,
            certifications, projects, interviews and the job market.
            Aura combines its knowledge base, conversation memory,
            external tools and real AI reasoning.
        </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# QUICK QUESTIONS
# ============================================================

st.markdown(
    '<div class="quick-title">Try asking Aura</div>',
    unsafe_allow_html=True,
)

quick_prompts = [
    "What cybersecurity skills should I learn?",
    "Create a 6-month cybersecurity roadmap",
    "Compare VAPT and GRC careers",
    "What free resources should I use?",
]

cols = st.columns(4)

for i, prompt in enumerate(quick_prompts):

    with cols[i]:

        if st.button(
            prompt,
            key=f"quick_{i}",
            use_container_width=True,
        ):

            st.session_state.pending_prompt = prompt

            st.rerun()


# ============================================================
# INFORMATION CARDS
# ============================================================

c1, c2, c3 = st.columns(3)

with c1:

    st.markdown(
        """
        <div class="aura-card">

            <div class="icon">🎯</div>

            <h3>Career Direction</h3>

            <p>
                Identify suitable career paths,
                compare roles and understand
                the skills employers expect.
            </p>

        </div>
        """,
        unsafe_allow_html=True,
    )


with c2:

    st.markdown(
        """
        <div class="aura-card">

            <div class="icon">🧠</div>

            <h3>Skill Development</h3>

            <p>
                Build structured learning plans,
                identify skill gaps and discover
                practical projects.
            </p>

        </div>
        """,
        unsafe_allow_html=True,
    )


with c3:

    st.markdown(
        """
        <div class="aura-card">

            <div class="icon">🚀</div>

            <h3>Career Execution</h3>

            <p>
                Prepare for interviews, improve
                your resume and understand
                current career opportunities.
            </p>

        </div>
        """,
        unsafe_allow_html=True,
    )


st.divider()


# ============================================================
# CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"],
        avatar="✦" if message["role"] == "assistant" else "👤",
    ):

        st.markdown(message["content"])


# ============================================================
# GET USER PROMPT
# ============================================================

pending_prompt = st.session_state.pop(
    "pending_prompt",
    None,
)

user_prompt = st.chat_input(
    "Ask Aura anything about your career, skills or learning..."
)


if pending_prompt:

    user_prompt = pending_prompt


# ============================================================
# PROCESS AI REQUEST
# ============================================================

if user_prompt:

    user_prompt = user_prompt.strip()

    if not user_prompt:
        st.stop()


    # --------------------------------------------------------
    # User message
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_prompt,
        }
    )


    with st.chat_message(
        "user",
        avatar="👤",
    ):

        st.markdown(user_prompt)


    # --------------------------------------------------------
    # AI response
    # --------------------------------------------------------

    with st.chat_message(
        "assistant",
        avatar="✦",
    ):

        with st.spinner(
            "Aura is thinking..."
        ):

            try:

                # --------------------------------------------
                # RAG
                # --------------------------------------------

                try:

                    retrieved_context = retrieve_context(
                        user_prompt,
                        k=4,
                    )

                except Exception as rag_error:

                    print(
                        "RAG error:",
                        repr(rag_error),
                    )

                    retrieved_context = ""


                # --------------------------------------------
                # AI AGENT
                # --------------------------------------------

                response = run_aura(

                    user_query=user_prompt,

                    memory=st.session_state.aura_memory,

                    retrieved_context=retrieved_context,

                    human_approved=False,
                )


                # --------------------------------------------
                # Store memory
                # --------------------------------------------

                st.session_state.aura_memory.add(
                    "user",
                    user_prompt,
                )

                st.session_state.aura_memory.add(
                    "assistant",
                    response,
                )


                # --------------------------------------------
                # Display
                # --------------------------------------------

                st.markdown(response)


                # --------------------------------------------
                # Save chat
                # --------------------------------------------

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": response,
                    }
                )


            except Exception as exc:

                error_message = (
                    "⚠️ **Aura encountered an error.**\n\n"
                    f"`{str(exc)}`"
                )

                st.error(
                    error_message
                )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message,
                    }
                )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        "## ✦ AuraAI"
    )

    st.caption(
        "AI Career & Skills Navigator"
    )

    st.divider()

    st.markdown(
        "### AI Engine"
    )

    if groq_key:

        st.success(
            "Groq API connected"
        )

    else:

        st.error(
            "Groq API key missing"
        )


    st.markdown(
        "### Knowledge"
    )

    st.info(
        "FAISS RAG knowledge base enabled."
    )


    st.markdown(
        "### Memory"
    )

    st.info(
        "Short-term conversation memory enabled."
    )


    st.divider()


    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True,
    ):

        st.session_state.messages = []

        st.session_state.aura_memory.clear()

        st.rerun()


    st.markdown(
        """
        <div style="
            margin-top:30px;
            color:#7186aa;
            font-size:.75rem;
            line-height:1.6;
        ">
        Aura provides career-development guidance
        and should not be treated as a guarantee of
        employment or other professional outcomes.
        </div>
        """,
        unsafe_allow_html=True,
    )
