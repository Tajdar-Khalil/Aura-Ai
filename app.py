import os

# --- MUST be set BEFORE importing transformers/sentence_transformers ---
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"
# This prevents transformers from trying to import vision modules that need torchvision
os.environ["TRANSFORMERS_NO_TORCHVISION"] = "1"

import re
import json
import base64
from io import BytesIO

import streamlit as st
import numpy as np
import faiss
from groq import Groq
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
from docx import Document

# --- Firebase Integration ---
# Ensure firebase_db_py.py is in the same directory
import firebase_db_py as fdb

# ============================================================
# Learning Accelerator – Adaptive AI Tutor
# Enterprise / Minimalist SaaS Architecture (with Firebase)
# ============================================================

APP_TITLE = "Learning Accelerator"
APP_SUBTITLE = "Adaptive Academic Tutoring System"
DEFAULT_MODEL = "openai/gpt-oss-20b"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
MAX_FILE_MB = 10
CHUNK_SIZE = 900
CHUNK_OVERLAP = 120
TOP_K = 5

st.set_page_config(
    page_title=f"{APP_TITLE} | {APP_SUBTITLE}",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Firebase functions are aliased for cleaner app.py code
fb_sign_up = fdb.sign_up
fb_sign_in = fdb.sign_in
save_document_record = fdb.save_document_record
delete_document_record = fdb.delete_document_record
get_user_documents = fdb.get_user_documents

# Professional Minimalist CSS (SaaS Design System)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

html:has(.hero-main-title), body:has(.hero-main-title) {
    overflow-y: auto !important;
    height: 100vh !important;
    max-height: 100vh !important;
}
html, body {
    margin: 0 !important;
    padding: 0 !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #0f172a;
}

body:has(.hero-main-title) #root,
body:has(.hero-main-title) .stApp,
body:has(.hero-main-title) [data-testid="stAppViewContainer"], 
body:has(.hero-main-title) .stAppViewContainer, 
body:has(.hero-main-title) section.main,
body:has(.hero-main-title) .stMain,
body:has(.hero-main-title) [data-testid="stMain"] {
    overflow-y: auto !important;
    height: 100vh !important;
    max-height: 100vh !important;
}

#root,
.stApp,
[data-testid="stAppViewContainer"], 
.stAppViewContainer, 
section.main,
.stMain,
[data-testid="stMain"] {
    padding: 0px !important;
    margin: 0px !important;
    background-color: #f7fafe !important;
    background-image: 
        radial-gradient(at 15% 15%, #e8f2fe 0px, transparent 48%),
        radial-gradient(at 88% 18%, #edf5ff 0px, transparent 45%),
        radial-gradient(at 50% 90%, #eaf2fd 0px, transparent 55%) !important;
}

div.block-container,
div[data-testid="stMainBlockContainer"],
.stMainBlockContainer,
div[class*="stMainBlockContainer"],
div[class*="block-container"],
div[class*="e15ve43o4"] {
    padding-top: 0px !important;
    padding-bottom: 0px !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
    margin-top: 0px !important;
    margin-bottom: 0px !important;
    max-width: 1280px !important;
}

body:has(.hero-main-title) div.block-container,
body:has(.hero-main-title) div[data-testid="stMainBlockContainer"],
body:has(.hero-main-title) .stMainBlockContainer,
body:has(.hero-main-title) div[class*="stMainBlockContainer"],
body:has(.hero-main-title) div[class*="block-container"],
body:has(.hero-main-title) div[class*="e15ve43o4"] {
    height: 100vh !important;
    max-height: 100vh !important;
    overflow-y: auto !important;
}

[data-testid="stToolbarActions"],
[data-testid="stAppDeployButton"],
[data-testid="stMainMenu"],
[data-testid="stMainMenuButton"],
.stDeployButton,
div[data-testid="stDecoration"],
div[data-testid="stStatusWidget"],
#MainMenu {
    display: none !important;
    visibility: hidden !important;
    height: 0px !important;
    min-height: 0px !important;
    max-height: 0px !important;
    padding: 0px !important;
    margin: 0px !important;
}

header[data-testid="stHeader"],
.stAppHeader,
div[data-testid="stHeader"],
header,
div[data-testid="stToolbar"],
.stAppToolbar {
    background: transparent !important;
    box-shadow: none !important;
    border: none !important;
    z-index: 9999999 !important;
    height: 0px !important;
    min-height: 0px !important;
    overflow: visible !important;
    pointer-events: none !important;
}

button[data-testid="stExpandSidebarButton"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    pointer-events: auto !important;
    position: fixed !important;
    top: 18px !important;
    left: 18px !important;
    background-color: #ffffff !important;
    border-radius: 50% !important;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.12) !important;
    width: 38px !important;
    height: 38px !important;
    justify-content: center !important;
    align-items: center !important;
    z-index: 9999999 !important;
    border: 1.5px solid #e2e8f0 !important;
    color: #2563eb !important;
    transition: all 0.2s ease !important;
    cursor: pointer !important;
}

button[data-testid="stExpandSidebarButton"]:hover {
    background-color: #eff6ff !important;
    border-color: #bfdbfe !important;
    transform: scale(1.06) !important;
}

button[data-testid="stExpandSidebarButton"] svg {
    color: #2563eb !important;
    fill: #2563eb !important;
    width: 20px !important;
    height: 20px !important;
}

body:has(.hero-main-title) section[data-testid="stSidebar"],
body:has(.hero-main-title) button[data-testid="stExpandSidebarButton"],
body:has(.hero-main-title) div[data-testid="collapsedControl"] {
    display: none !important;
}

div[data-testid="stHorizontalBlock"]:has(.brand-group) {
    position: fixed !important;
    top: 0px !important;
    left: 0px !important;
    right: 0px !important;
    width: 100vw !important;
    height: 56px !important;
    background: #ffffff !important;
    border-bottom: 1.5px solid #e2e8f0 !important;
    border-radius: 0px !important;
    padding: 0px 2.5rem !important;
    margin: 0px !important;
    z-index: 999999 !important;
    display: flex !important;
    align-items: center !important;
    box-shadow: 0 1px 4px rgba(15, 23, 42, 0.04) !important;
}

div[data-testid="stHorizontalBlock"]:has(.brand-group) div[data-testid="stColumn"] {
    display: flex !important;
    align-items: center !important;
}

.brand-group { display: flex; align-items: center; gap: 10px; }
.brand-logo-icon {
    width: 34px; height: 34px; border-radius: 9px;
    background: #eff6ff; display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.brand-title-main { font-size: 15.5px; font-weight: 800; color: #0f172a; line-height: 1.15; letter-spacing: -0.02em; }
.brand-subtitle-main { font-size: 11px; color: #64748b; font-weight: 500; }

.header-highlight-pill {
    display: inline-flex; align-items: center; gap: 6px;
    background: #eff6ff; border: 1px solid #bfdbfe; color: #2563eb;
    border-radius: 9999px; padding: 4px 14px; font-size: 11.5px; font-weight: 600;
    letter-spacing: 0.01em; box-shadow: 0 1px 2px rgba(37, 99, 235, 0.04);
}

.nav-switch-label {
    font-size: 12px; color: #475569; font-weight: 500;
    text-align: right; line-height: 32px; margin: 0; padding: 0;
}

div[data-testid="stHorizontalBlock"]:has(.brand-group) button {
    background-color: #ffffff !important; border: 1.5px solid #2563eb !important;
    color: #2563eb !important; border-radius: 9999px !important;
    font-weight: 600 !important; font-size: 12px !important;
    padding: 0 16px !important; height: 32px !important; line-height: 30px !important;
    box-shadow: 0 1px 2px rgba(37, 99, 235, 0.05) !important;
    transition: all 0.15s ease-in-out !important;
}
div[data-testid="stHorizontalBlock"]:has(.brand-group) button:hover {
    background-color: #eff6ff !important; border-color: #1d4ed8 !important; color: #1d4ed8 !important;
}

div[data-testid="stHorizontalBlock"]:has(.hero-main-title) {
    margin-top: 66px !important; padding-top: 0px !important; align-items: flex-start !important;
}

.hero-left-wrapper { position: relative; width: 100%; height: calc(100vh - 80px); }
.hero-main-title {
    font-size: 38px !important; font-weight: 900 !important; line-height: 1.2 !important;
    color: #0f172a !important; letter-spacing: -0.03em !important;
    margin-bottom: 12px !important; margin-top: 0px !important;
    position: relative; z-index: 10;
}
.hero-main-title .highlight-blue { color: #2563eb; }
.hero-lead-desc {
    font-size: 16px !important; color: #475569 !important; line-height: 1.5 !important;
    margin-bottom: 24px !important; max-width: 480px !important;
    position: relative; z-index: 10;
}

.feature-stack {
    display: flex; flex-direction: column; gap: 12px; margin-bottom: 24px;
    position: relative; z-index: 10;
}
.feature-card-item { display: flex; align-items: center; gap: 12px; }
.feature-round-icon {
    width: 36px; height: 36px; border-radius: 50%; background: #eff6ff;
    display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.feature-title-txt { font-size: 15px; font-weight: 700; color: #0f172a; }
.feature-desc-txt { font-size: 13px; color: #64748b; margin-top: 0px; }

.student-hero-container {
    width: 100%; position: absolute; bottom: -10px; left: 0; z-index: 1;
    display: flex; align-items: flex-end; justify-content: center;
}
.student-hero-container img {
    max-height: 480px; width: auto; max-width: 100%; object-fit: contain; display: block;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff !important; border-radius: 16px !important;
    border: 1px solid #e2e8f0 !important; padding: 12px 18px !important;
    box-shadow: 0 8px 20px -4px rgba(15, 23, 42, 0.04) !important;
}

.auth-card-header { display: flex; align-items: center; gap: 8px; margin-bottom: 3px; }
.auth-avatar-icon {
    width: 30px; height: 30px; border-radius: 50%; background: #eff6ff;
    display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.auth-header-title { font-size: 16px; font-weight: 800; color: #0f172a; letter-spacing: -0.02em; line-height: 1.15; }
.auth-header-desc { font-size: 11px; color: #64748b; margin-top: 0px; line-height: 1.2; }

.form-section-title {
    font-size: 11.5px; font-weight: 700; color: #0f172a;
    letter-spacing: -0.01em; margin-top: 4px; margin-bottom: 1px;
}

div[data-testid="stTextInput"] { margin-bottom: 0px !important; }
div[data-testid="stTextInput"] label p,
div[data-testid="stSelectbox"] label p {
    font-size: 11px !important; font-weight: 600 !important;
    color: #334155 !important; margin-bottom: 1px !important;
}
div[data-testid="stTextInput"] input {
    border-radius: 7px !important; border: 1.5px solid #e2e8f0 !important;
    font-size: 12px !important; padding: 0.25rem 0.55rem !important;
    background-color: #ffffff !important; color: #0f172a !important; height: 32px !important;
    transition: all 0.15s ease-in-out !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #2563eb !important; box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.12) !important;
}

div[data-baseweb="select"] > div {
    border-radius: 7px !important; border: 1.5px solid #e2e8f0 !important;
    background-color: #ffffff !important; min-height: 32px !important;
    height: 32px !important; font-size: 12px !important;
    transition: all 0.15s ease-in-out !important;
}

button[kind="primary"] {
    background-color: #2563eb !important; border: 1px solid #2563eb !important;
    color: #ffffff !important; font-weight: 600 !important; font-size: 13px !important;
    border-radius: 8px !important; height: 35px !important;
    box-shadow: 0 2px 8px rgba(37, 99, 235, 0.2) !important;
    transition: all 0.15s ease-in-out !important; margin-top: 3px !important;
}
button[kind="primary"]:hover { background-color: #1d4ed8 !important; border-color: #1d4ed8 !important; }

button[kind="secondary"] {
    background-color: #ffffff !important; border: 1.5px solid #e2e8f0 !important;
    color: #334155 !important; font-weight: 500 !important; font-size: 11.5px !important;
    border-radius: 7px !important; height: 32px !important;
    transition: all 0.15s ease-in-out !important;
}
button[kind="secondary"]:hover { background-color: #f8fafc !important; border-color: #cbd5e1 !important; }

div[data-testid="stChatMessage"] {
    background-color: #ffffff !important; border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important; padding: 1rem 1.25rem !important;
    margin-bottom: 0.85rem !important;
    box-shadow: 0 1px 2px 0 rgba(15, 23, 42, 0.03) !important;
}

.stat-card {
    background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px;
    padding: 20px; display: flex; align-items: center; gap: 16px;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
}
.stat-icon {
    width: 48px; height: 48px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center; font-size: 20px;
}
.stat-icon.blue { background: #e0f2fe; color: #0284c7; }
.stat-icon.green { background: #dcfce7; color: #16a34a; }
.stat-icon.purple { background: #f3e8ff; color: #9333ea; }
.stat-icon.orange { background: #ffedd5; color: #ea580c; }
.stat-title { font-size: 13px; color: #64748b; font-weight: 500; margin-bottom: 4px; }
.stat-value { font-size: 24px; font-weight: 700; color: #0f172a; line-height: 1; }

.dash-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
.dash-title { font-size: 24px; font-weight: 800; color: #0f172a; line-height: 1.2; }
.dash-subtitle { font-size: 14px; color: #64748b; }
.bell-icon {
    width: 36px; height: 36px; border-radius: 50%; border: 1px solid #e2e8f0;
    display: flex; align-items: center; justify-content: center; color: #475569;
}
.profile-badge { display: flex; align-items: center; gap: 12px; }
.profile-avatar {
    width: 40px; height: 40px; border-radius: 50%; background: #2563eb; color: white;
    font-weight: 700; display: flex; align-items: center; justify-content: center;
}
</style>
""", unsafe_allow_html=True)

# ---------- Session state ----------
def init_state():
    defaults = {
        "authenticated": False,
        "auth_mode": "signup",
        "current_page": "Dashboard",
        "current_user": None,
        "chat_sessions": {},
        "current_chat_id": None,
        "chunks": [],
        "chunk_sources": [],
        "faiss_index": None,
        "embeddings_ready": False,
        "quiz": [],
        "quiz_answers": {},
        "score_history": [],
        "plan": "",
        "model": DEFAULT_MODEL,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_state()

def get_hero_student_base64():
    for fname in ["student_clean_opt.png", "student_clean.png", "hero_student.png"]:
        path = os.path.join(os.path.dirname(__file__), "assets", fname)
        if os.path.exists(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
    return ""

def get_groq_key():
    try:
        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except Exception:
        pass
    return os.getenv("GROQ_API_KEY", "")

def get_client():
    key = get_groq_key()
    if not key:
        return None
    return Groq(api_key=key)

@st.cache_resource(show_spinner=False)
def load_embedder():
    try:
        return SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
    except Exception:
        try:
            return SentenceTransformer(EMBED_MODEL, local_files_only=True)
        except Exception:
            return SentenceTransformer(EMBED_MODEL)

def extract_text(uploaded_file):
    name = uploaded_file.name.lower()
    raw = uploaded_file.getvalue()

    if len(raw) > MAX_FILE_MB * 1024 * 1024:
        raise ValueError(f"{uploaded_file.name} exceeds {MAX_FILE_MB} MB limit.")

    if name.endswith(".pdf"):
        reader = PdfReader(BytesIO(raw))
        pages = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                pages.append(f"[Page {i + 1}]\n{text}")
        return "\n\n".join(pages)

    if name.endswith(".docx"):
        doc = Document(BytesIO(raw))
        parts = [p.text for p in doc.paragraphs if p.text.strip()]
        for table in doc.tables:
            for row in table.rows:
                parts.append(" | ".join(cell.text.strip() for cell in row.cells))
        return "\n".join(parts)

    if name.endswith(".txt") or name.endswith(".md"):
        return raw.decode("utf-8", errors="ignore")

    raise ValueError("Supported formats: PDF, DOCX, TXT, MD.")

def chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            boundary = max(
                text.rfind(". ", start, end),
                text.rfind("? ", start, end),
                text.rfind("! ", start, end),
            )
            if boundary > start + int(size * 0.55):
                end = boundary + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break
        start = max(end - overlap, start + 1)

    return chunks

def build_index(files_uploaded):
    all_chunks = []
    sources = []

    for file in files_uploaded:
        text = extract_text(file)
        chunks = chunk_text(text)
        if not chunks:
            continue
        all_chunks.extend(chunks)
        sources.extend([file.name] * len(chunks))
        if st.session_state.current_user and "uid" in st.session_state.current_user:
            save_document_record(
                st.session_state.current_user["uid"], 
                file.name, 
                f"{len(file.getvalue()) / 1024:.1f} KB"
            )

    if not all_chunks:
        raise ValueError("No readable text found in the uploaded documents.")

    model = load_embedder()
    vectors = model.encode(
        all_chunks,
        batch_size=32,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    ).astype("float32")

    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)

    st.session_state.chunks = all_chunks
    st.session_state.chunk_sources = sources
    st.session_state.faiss_index = index
    st.session_state.embeddings_ready = True

def retrieve(query, k=TOP_K):
    if not st.session_state.embeddings_ready:
        return []

    model = load_embedder()
    q = model.encode(
        [query],
        normalize_embeddings=True,
        convert_to_numpy=True,
    ).astype("float32")

    k = min(k, len(st.session_state.chunks))
    scores, ids = st.session_state.faiss_index.search(q, k)

    results = []
    for score, idx in zip(scores[0], ids[0]):
        if idx >= 0:
            results.append({
                "text": st.session_state.chunks[idx],
                "source": st.session_state.chunk_sources[idx],
                "score": float(score),
            })
    return results

def run_planner_agent(topic, target_date, hours, level, style, selected_doc=None):
    client = get_client()
    if not client:
        return "System notice: Groq API key is not configured."

    context_str = ""
    if st.session_state.embeddings_ready and st.session_state.chunks:
        if selected_doc and selected_doc not in ["All Uploaded Documents", "Custom Subject / General Topic"]:
            doc_chunks = [c for c, s in zip(st.session_state.chunks, st.session_state.chunk_sources) if s == selected_doc]
            sample_chunks = doc_chunks[:8]
            context_str = "\n\n".join([f"[{selected_doc}]\n{c}" for c in sample_chunks])
        else:
            contexts = retrieve(topic, k=6)
            if contexts:
                context_str = "\n\n".join([f"[{c['source']}]\n{c['text']}" for c in contexts])

    student_name = st.session_state.current_user["name"] if st.session_state.current_user else "Student"
    prompt = f"""
You are the Curriculum Planner in this academic tutoring system.
Create a detailed, objective, and structured study schedule for the candidate directly based on the provided course material/syllabus when available.

Candidate: {student_name}
Subject / Target Goal: {topic}
Target Timeline: {target_date}
Available Daily Commitment: {hours} hours
Proficiency Level: {level}
Preferred Learning Method: {style}

Reference Course Document Content:
{context_str if context_str else "No uploaded course documents selected. Formulate a structured study plan based on standard academic curriculum."}
"""
    res = client.chat.completions.create(
        model=st.session_state.model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return res.choices[0].message.content

def run_explainer_agent(user_question):
    client = get_client()
    if not client:
        return "System notice: Groq API key is not configured."

    contexts = retrieve(user_question, k=TOP_K)
    context_str = ""
    if contexts:
        ctx_blocks = []
        for i, c in enumerate(contexts, 1):
            ctx_blocks.append(f"[Document Reference {i} | Source: {c['source']}]\n{c['text']}")
        context_str = "\n\n".join(ctx_blocks)

    system_prompt = "You are the Learning Accelerator's AI Assistant, designed to help students learn, understand concepts, and navigate their study materials."
    user_prompt = f"Student Inquiry:\n{user_question}\n\nRetrieved Document Context:\n{context_str if context_str else 'No course materials indexed.'}"

    res = client.chat.completions.create(
        model=st.session_state.model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )
    return res.choices[0].message.content

def run_quiz_agent(topic_or_context, num_q=3):
    client = get_client()
    if not client:
        return []

    contexts = retrieve(topic_or_context, k=3)
    ref_text = "\n".join([c["text"] for c in contexts]) if contexts else topic_or_context

    prompt = f"""
Generate an assessment of {num_q} multiple choice questions based on this study content:
Content:
{ref_text[:3000]}

Return valid JSON with this exact schema:
[
  {{
    "question": "Question text here?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "answer_index": 0,
    "explanation": "Clear explanation of the correct choice."
  }}
]
"""
    res = client.chat.completions.create(
        model=st.session_state.model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    text = res.choices[0].message.content
    try:
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return json.loads(text)
    except Exception:
        return []

def run_progress_coach():
    client = get_client()
    if not client:
        return "System notice: Groq API key is not configured."

    history = st.session_state.score_history
    student_name = st.session_state.current_user["name"] if st.session_state.current_user else "Student"
    if not history:
        return f"No assessment records exist for {student_name} in the current session."

    prompt = f"Review candidate evaluation logs and provide diagnostic feedback:\n{json.dumps(history, indent=2)}"
    res = client.chat.completions.create(
        model=st.session_state.model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return res.choices[0].message.content


# ============================================================
# VIEW 1: AUTHENTICATION
# ============================================================
if not st.session_state.authenticated:
    col_nav_brand, col_nav_pill, col_nav_switch = st.columns([1.5, 1.2, 1.3])
    with col_nav_brand:
        st.markdown(f"""
        <div class="brand-group">
            <div class="brand-logo-icon">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="#2563eb">
                    <path d="M12 3L1 9l11 6 9-4.91V17h2V9L12 3z M5 13.18v4L12 21l7-3.82v-4L12 17l-7-3.82z"/>
                </svg>
            </div>
            <div>
                <div class="brand-title-main">{APP_TITLE}</div>
                <div class="brand-subtitle-main">{APP_SUBTITLE}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_nav_pill:
        st.markdown("""
        <div style="display:flex; justify-content:center; align-items:center; height:100%;">
            <div class="header-highlight-pill">
                <span>For a Brighter Academic Future</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_nav_switch:
        if st.session_state.auth_mode == "signup":
            col_sw_txt, col_sw_btn = st.columns([1.2, 1])
            with col_sw_txt:
                st.markdown('<div class="nav-switch-label">Already have an account?</div>', unsafe_allow_html=True)
            with col_sw_btn:
                if st.button("Sign In", key="top_signin_pill", use_container_width=True):
                    st.session_state.auth_mode = "signin"
                    st.rerun()
        else:
            col_sw_txt, col_sw_btn = st.columns([1.2, 1])
            with col_sw_txt:
                st.markdown('<div class="nav-switch-label">New student?</div>', unsafe_allow_html=True)
            with col_sw_btn:
                if st.button("Sign Up", key="top_signup_pill", use_container_width=True):
                    st.session_state.auth_mode = "signup"
                    st.rerun()

    col_hero, col_card = st.columns([1.08, 1.28], gap="large")

    with col_hero:
        hero_b64 = get_hero_student_base64()
        img_html = f'<img src="data:image/png;base64,{hero_b64}" alt="Student" />' if hero_b64 else ''
        st.markdown(f"""
<div class="hero-left-wrapper">
<div class="hero-main-title">
Learn Smarter<br>
<span class="highlight-blue">Grow Faster</span>
</div>
<div class="hero-lead-desc">
AI-powered academic tutoring system designed to help you achieve your goals securely with Firebase.
</div>
<div class="student-hero-container">
{img_html}
</div>
</div>
""", unsafe_allow_html=True)

    with col_card:
        with st.container(border=True):
            if st.session_state.auth_mode == "signup":
                st.markdown("""
                <div class="auth-card-header">
                    <div class="auth-avatar-icon">
                        <svg width="20" height="20" fill="none" stroke="#2563eb" stroke-width="2" viewBox="0 0 24 24">
                            <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><line x1="20" y1="8" x2="20" y2="14"/><line x1="23" y1="11" x2="17" y2="11"/>
                        </svg>
                    </div>
                    <div>
                        <div class="auth-header-title">Create Your Student Account</div>
                        <div class="auth-header-desc">Register securely with Firebase backend.</div>
                    </div>
                </div>
                <div class="form-section-title">Personal Information</div>
                """, unsafe_allow_html=True)

                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    reg_name = st.text_input("Full Name", placeholder="Full Name", key="signup_name")
                with col_c2:
                    reg_id = st.text_input("Student ID", placeholder="Student ID", key="signup_id")

                col_c3, col_c4 = st.columns(2)
                with col_c3:
                    dept_choices = [
                        "Select Department",
                        "Computer Science",
                        "Software Engineering",
                        "Artificial Intelligence & Data Science",
                        "Information Technology",
                        "Electrical Engineering",
                        "Business Administration",
                        "General Studies"
                    ]
                    reg_dept = st.selectbox("Department", dept_choices, key
