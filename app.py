import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="AuraAI - AI Career & Skills Navigator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Dark Theme & SaaS Styling
st.markdown("""
    <style>
    .stApp {
        background-color: #0b0f19;
        color: #f8fafc;
    }
    sidebar[data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #1f2937;
    }
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #111827;
        color: #94a3b8;
        text-align: center;
        padding: 10px;
        font-size: 12px;
        border-top: 1px solid #1f2937;
        z-index: 100;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Sidebar Navigation
with st.sidebar:
    st.markdown("### ⚛️ AuraAI")
    st.caption("AI Career & Skills Navigator")
    st.divider()
    
    selected_page = st.radio(
        "Navigation",
        ["Chat with Aura", "Career Roadmap", "Skills Analysis", "About Aura AI", "Contact & Support"],
        label_visibility="collapsed"
    )
    
    st.divider()
    st.markdown("**Your Progress**")
    st.progress(0.68, text="Career Growth Journey (68%)")

# 3. Main Content Router
if selected_page == "Chat with Aura":
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("Chat with Aura")
        st.caption("Your AI Career Coach powered by Groq & CrewAI")
        
        # Chat Messages Area
        with st.chat_message("user"):
            st.write("What skills should I learn to become a Web Application Security Engineer?")
            
        with st.chat_message("assistant", avatar="🤖"):
            st.write("Great choice! Becoming a Web Application Security Engineer requires foundational security knowledge, hands-on tool practice, and continuous learning[cite: 2]:")
            st.markdown("""
            * **1. Core Security Skills:** OWASP Top 10, secure coding practices, authentication protocols[cite: 2].
            * **2. Technical & Tools:** Burp Suite, OWASP ZAP, Nmap, Wireshark.
            * **3. Supporting Knowledge:** Linux administration, cloud security basics.
            """)
            
        # Chat Input Box
        user_input = st.chat_input("Type your message to Aura...")
        if user_input:
            st.write(f"User sent: {user_input}")

    with col2:
        # Right Assistant Panel (Matching Design Reference)
        st.markdown("### 🌟 Aura AI Guide")
        st.info('"Big dreams need a plan. I\'m here to help you build yours."')
        st.markdown("**Model Engine:** GPT-OSS-120B[cite: 2]")
        st.markdown("**Knowledge Base:** FAISS RAG[cite: 2]")
        st.markdown("**Workflow:** CrewAI Agentic[cite: 2]")

elif selected_page == "About Aura AI":
    st.header("About Aura AI & Architecture")
    st.write("""
    **AI Career Skills Navigator** is an intelligent AI-agent-based career guidance application designed to help users explore career paths, identify skill gaps, and make informed development decisions[cite: 2]. 
    The system uses the **Aura AI Agent** powered by **CrewAI** and **Groq LLM (GPT-OSS-120B)**[cite: 2].
    
    ### Key Technical Components:
    * **RAG & FAISS Vector Database:** Retrieves relevant knowledge using project-specific vector stores and embeddings[cite: 2].
    * **Agentic Workflow:** Follows a strict *Goal → Decide → Act → Observe → Complete* cycle[cite: 2].
    * **Human-in-the-Loop (HITL):** Selectively requests user confirmation for consequential actions and custom preferences[cite: 2].
    """)

elif selected_page == "Contact & Support":
    st.header("Contact & Support")
    st.write("Have questions or feedback? Reach out to the developer directly.")
    
    with st.form("contact_form"):
        name = st.text_input("Your Name")
        email = st.text_input("Your Email")
        message = st.text_area("Message")
        submitted = st.form_submit_button("Send Message")
        if submitted:
            st.success("Message sent successfully!")

# 4. Global Copyright Footer
st.markdown("""
    <div class="footer">
        &copy; 2026 AuraAI — AI Career Skills Navigator. All rights reserved. Designed & developed by Tajdar Khalil.
    </div>
""", unsafe_allow_html=True)
