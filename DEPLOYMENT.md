# AuraAI UI integration

`app.py` is now the Streamlit deployment entrypoint for the new Aura dashboard UI.
The previous Streamlit entrypoint is preserved unchanged as `app_original_streamlit.py`.
The original AI modules (`agent.py`, `memory.py`, `rag.py`, `security.py`, `tools.py`, `firebase_service.py`) remain in place and are imported by the new UI.

## GitHub structure

```text
AuraAI/
├── app.py                         # NEW main Streamlit UI
├── app_original_streamlit.py      # ORIGINAL app.py preserved
├── agent.py                       # ORIGINAL CrewAI agent
├── firebase_service.py            # ORIGINAL Firebase auth/FCM service
├── memory.py                      # ORIGINAL short-term memory
├── rag.py                          # ORIGINAL FAISS RAG module
├── security.py                    # ORIGINAL security helpers
├── tools.py                        # ORIGINAL 4 controlled tools
├── system_prompt.txt              # ORIGINAL agent prompt
├── knowledge_base.json             # ORIGINAL KB
├── data/
│   └── knowledge_base.json         # deployment copy used by original rag.py path
├── services/
│   └── profile_service.py          # persistent progress/recent-chat profile layer
├── ui/
│   └── styles.py                   # dashboard/home visual system
├── assets/
│   └── aura_avatar.jpg             # Aura artwork
├── .streamlit/
│   └── secrets.toml                # local only; never commit
├── requirements.txt
├── runtime.txt
└── README.md
```

## Authentication flow

Home → **Explore Aura AI** → Login/Register dialog → Firebase Authentication → Dashboard.

A new Firebase account starts at **0% progress**. Progress is increased only when the user actually completes dashboard interactions such as Chat, Roadmap, Skills, Opportunities, Resources, and setting a goal. When Firestore is configured, the progress and recent chats persist by Firebase UID.

The profile avatar uses the user's email to request a Gravatar/identicon. Firebase email/password authentication itself does not provide a photo URL by default.

## Deployment

Deploy with Streamlit using `app.py` as the entrypoint. Python 3.12 is retained.

Keep Firebase Admin credentials and the Groq key in Streamlit Secrets; do not put service-account JSON or private credentials in GitHub.

The original `rag.py` expects `data/knowledge_base.json`, so the repository now includes a deployment copy there without changing the original `rag.py`.
