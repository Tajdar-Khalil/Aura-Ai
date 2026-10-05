# AuraAI — AI Career & Skills Navigator

<div align="center">

![AuraAI Banner](assets/aura_avatar.jpg)

**An enterprise-grade, agentic AI career mentor powered by Groq GPT-OSS-120B, CrewAI, FAISS Vector RAG, and OWASP-aligned security guardrails.**

[![Python Version](https://img.shields.io/badge/python-3.12-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Groq Powered](https://img.shields.io/badge/Groq-GPT--OSS--120B-f55036.svg?style=for-the-badge&logo=fastapi&logoColor=white)](https://groq.com/)
[![CrewAI](https://img.shields.io/badge/Agentic%20Framework-CrewAI%20v1.0-orange.svg?style=for-the-badge)](https://crewai.com/)
[![FAISS RAG](https://img.shields.io/badge/Vector%20Search-FAISS%20%2B%20MiniLM-0ea5e9.svg?style=for-the-badge)](https://github.com/facebookresearch/faiss)
[![Security Guardrails](https://img.shields.io/badge/Security-OWASP%20LLM%20Top%2010-10b981.svg?style=for-the-badge)](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
[![UI](https://img.shields.io/badge/Frontend-Dark%20Glassmorphism-6366f1.svg?style=for-the-badge)](https://streamlit.io/)

[Live Demo](#quick-start) • [Architecture](#system-architecture) • [Features](#key-capabilities) • [Installation](#installation--setup) • [Configuration](#configuration--environment) • [Contact](#contact--support)

</div>

---

## 📌 Executive Summary

**AuraAI** is a high-performance, empathetic, and evidence-grounded AI Career & Skills Navigator designed to help professionals and aspiring engineers bridge critical skill gaps, discover curated free learning materials, and navigate dynamic tech markets (such as Web Application Security, Cloud Architecture, DevSecOps, and GRC).

Built on top of a multi-tiered agent architecture, AuraAI combines **instant sub-second Groq LPUs**, **FAISS dense vector embeddings**, **four strictly governed external tools**, and a **custom markdown rendering engine** inside an ultra-sleek, responsive dark-navy glassmorphism dashboard.

---

## 🚀 Key Capabilities

### 🧠 1. Agentic AI Reasoning Core
* **Ultra-Fast Inference:** Powered by `openai/gpt-oss-120b` (with automated fallback to `openai/gpt-oss-20b` and `qwen/qwen3.8-27b`) hosted on Groq's LPU acceleration.
* **Goal–Decide–Act–Observe Lifecycle:** Follows strict agentic loop principles using CrewAI to determine whether external tooling or RAG context is required before answering.
* **Human-in-the-Loop (HITL):** Selective approval checkpoints for consequential career recommendations.

### 📚 2. Semantic FAISS Vector RAG
* **Dense Embeddings:** Utilizes `sentence-transformers/all-MiniLM-L6-v2` with `faiss-cpu` for real-time semantic retrieval across curated career knowledge bases.
* **Curated Ground Truth:** Anchors recommendations to reputable, verified educational paths, OWASP standards, and official documentation rather than unverified web hallucination.

### 🛠️ 3. Governed Tool Ecosystem
Aura is equipped with four strictly sandboxed external tools:
1. **`duckduckgo_search`** — Live public web search for current job openings and time-sensitive industry shifts.
2. **`wikipedia_search`** — Encyclopedic reference checks for stable technical definitions and standards.
3. **`requests_get`** — Hardened HTTPS JSON client with strict domain allowlisting (preventing SSRF and intranet pivoting).
4. **`calculate`** — Safe arithmetic evaluation for compensation packages and time-allocation math.

### 💬 4. Custom Clean-Markdown Engine
* **No Raw Hashes:** Automatically parses markdown headings (`#`, `##`, `###`) into modern styled headings without leaking raw `#` symbols.
* **Isolated Bullet Points:** Guarantees that every bullet item (`•`, `-`, `*`) and numbered point (`1.`, `2.`) renders on a fresh, distinct line with proper spacing.
* **Responsive HTML Tables:** Beautifully renders multi-column markdown tables (`| Phase | Goal | Deliverables | Timebox |`) into responsive, styled glassmorphism tables with zero messy pipe syntax.

### ⚡ 5. Dynamic Interactive Dashboard
* **Dynamic Recent Chats:** Real-time search history in the sidebar that automatically bubbles up recent questions to the top with clean timestamps.
* **Collapsible Dropdowns:** Interactive dropdown accordions for **AI Core Architecture** and **Quick Actions**, saving vertical space.
* **Single-Page Application (SPA):** Seamless routing between Landing Page, Auth (Login/Signup), and Dashboard with persistent state.

---

## 🏗️ System Architecture

```text
                                  ┌──────────────────────────────┐
                                  │      Client Web Browser      │
                                  │  (Streamlit / Flask / HTML)  │
                                  └──────────────┬───────────────┘
                                                 │
                                     User Query & Interactions
                                                 │
                                                 ▼
                                  ┌──────────────────────────────┐
                                  │   Security & Guardrails      │
                                  │  - Prompt Injection Defense  │
                                  │  - Input Validation          │
                                  └──────────────┬───────────────┘
                                                 │
                                  ┌──────────────┴───────────────┐
                                  ▼                              ▼
                    ┌───────────────────────────┐  ┌───────────────────────────┐
                    │     Memory Engine         │  │   FAISS Vector RAG        │
                    │  (Short-term context)     │  │ (sentence-transformers)   │
                    └─────────────┬─────────────┘  └─────────────┬─────────────┘
                                  │                              │
                                  └──────────────┬───────────────┘
                                                 ▼
                                  ┌──────────────────────────────┐
                                  │     CrewAI Aura Agent        │
                                  │  (Goal → Decide → Act)       │
                                  └──────────────┬───────────────┘
                                                 │
                                ┌────────────────┴────────────────┐
                                ▼                                 ▼
                 ┌─────────────────────────────┐   ┌─────────────────────────────┐
                 │       Governed Tools        │   │    Groq LPU Inference       │
                 │  - DuckDuckGo Search        │   │    - openai/gpt-oss-120b    │
                 │  - Wikipedia API            │   │    - openai/gpt-oss-20b     │
                 │  - Restricted HTTPS Get     │   │    - qwen/qwen3.8-27b       │
                 │  - Safe Math Calculator     │   └──────────────┬──────────────┘
                 └──────────────┬──────────────┘                  │
                                │                                 │
                                └────────────────┬────────────────┘
                                                 ▼
                                  ┌──────────────────────────────┐
                                  │   Output Sanitization        │
                                  │  - Bleach HTML Protection    │
                                  │  - Secret / Key Masking      │
                                  └──────────────┬───────────────┘
                                                 │
                                                 ▼
                                  ┌──────────────────────────────┐
                                  │  Custom Markdown Parser      │
                                  │  - Clean Headings & Tables   │
                                  │  - Un-clumped Bullet Points  │
                                  └──────────────┬───────────────┘
                                                 │
                                                 ▼
                                  ┌──────────────────────────────┐
                                  │   Rendered Chat Bubble       │
                                  │  (Dark Glassmorphism UI)     │
                                  └──────────────────────────────┘
```

---

## 📂 Project Directory Structure

```plaintext
Aura-Ai/
├── agent.py                 # CrewAI Agent definitions, system prompts & task runners
├── app.py                   # Streamlit production entrypoint
├── streamlit_app.py         # Complete unified Streamlit host with SPA wrapper
├── flask_app.py             # Flask REST backend (/api/chat, /api/auth)
├── database.py              # SQLite user registry & authentication store
├── rag.py                   # FAISS vector store creation, indexing & retrieval
├── tools.py                 # Governed external tools (Search, Wiki, API, Calc)
├── security.py              # OWASP LLM input validation, prompt injection defense
├── memory.py                # Sliding-window short-term conversation memory
├── system_prompt.txt        # Master behavioral and formatting prompt for Aura
├── requirements.txt         # Production Python dependencies
├── .env.example             # Configuration and API key template
├── dashboard.html           # Core responsive dark-mode Dashboard interface
├── index.html               # Public Marketing & Landing page
├── about.html               # Dedicated About page
├── contact.html             # Dedicated Contact & Inquiries page
├── signin.html              # Authentication sign-in portal
├── signup.html              # Authentication registration portal
├── templates/               # Flask Jinja2 mirroring templates
│   ├── dashboard.html
│   ├── index.html
│   ├── about.html
│   ├── contact.html
│   ├── signin.html
│   └── signup.html
└── static/
    ├── css/
    └── js/
        └── aura_auth.js     # Unified Client-Side State & Navigation Controller
```

---

## ⚙️ Installation & Setup

### Prerequisites
* **Python 3.12+** installed on your system.
* A valid **Groq API Key** ([Get one here from Groq Console](https://console.groq.com/keys)).
* (Optional) **Firebase Account** if using Firebase cloud authentication.

---

### Step 1: Clone the Repository
```bash
git clone https://github.com/usmancreation/Aura-Ai.git
cd Aura-Ai
```

---

### Step 2: Set Up Virtual Environment
```bash
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

---

### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

### Step 4: Configure Environment Variables
Create a `.env` file in the root directory by copying `.env.example`:
```bash
cp .env.example .env
```

Open `.env` and provide your credentials:
```env
# Mandatory: Groq API Key for live LLM intelligence
GROQ_API_KEY="gsk_your_groq_api_key_here"

# Model Selection
GROQ_MODEL="groq/openai/gpt-oss-120b"

# Optional: Firebase Config (if using Firebase instead of local SQLite)
FIREBASE_API_KEY=""
FIREBASE_PROJECT_ID=""
```

---

### Step 5: Launch the Application

#### Option A: Run via Streamlit (Recommended)
```bash
streamlit run streamlit_app.py --server.port 8501
```
*Access the interface at:* **`http://localhost:8501`**

#### Option B: Run via Flask
```bash
python flask_app.py
```
*Access the interface at:* **`http://localhost:5000`**

---

## 🛡️ Security & OWASP LLM Guardrails

AuraAI incorporates robust defenses aligned with the **OWASP Top 10 for Large Language Models**:

| Threat ID | Threat Name | AuraAI Mitigation |
|:---|:---|:---|
| **LLM01** | Prompt Injection | Pre-flight heuristic checks (`looks_like_prompt_injection`) detect override attempts, delimiters (`<\|im_start\|>`), and prompt leaking requests. |
| **LLM02** | Insecure Output Handling | All agent responses pass through `bleach.clean()` with strict HTML tag/attribute allowlists to eliminate stored XSS. |
| **LLM06** | Sensitive Information Disclosure | Guardrails explicitly reject queries attempting to inspect API keys, internal configs, environment variables, or private memory. |
| **LLM07** | Insecure Plugin/Tool Design | `requests_get` enforces an HTTPS host allowlist, preventing internal network reconnaissance (SSRF). |
| **LLM08** | Excessive Agency | Critical recommendations feature human checkpoints (HITL) before execution. Iteration and retry limits are strictly capped to 1. |

---

## 🎨 UI/UX Features & Design System

* **Color Palette:** Curated deep-navy space background (`#030a1f`), sapphire accents (`#1f8bff`), and vibrant cyan highlights (`#38bdf8`).
* **Typography:** `Plus Jakarta Sans` paired with clean monospaced font stacks for code snippets.
* **Responsive Collapsibles:** Instant toggle dropdowns for AI Core Architecture and Quick Actions with rotating SVG chevrons.
* **Dynamic Recent Searches:** Interactive sidebar tracking searches in real-time with automatic deduplication.

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1. **Fork** the project.
2. Create your feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a **Pull Request**.

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

## 📬 Contact & Support

* **Maintainer / Developer:** Muhammad Usman
* **Email:** [usmacreation804@gmail.com](mailto:usmacreation804@gmail.com)
* **GitHub Repository:** [https://github.com/usmancreation/Aura-Ai](https://github.com/usmancreation/Aura-Ai)
* **Headquarters:** Chakwal, Punjab, Pakistan

<div align="center">
  <sub>Built with ❤️ by the AuraAI Engineering Team. Powered by Groq & CrewAI.</sub>
</div>