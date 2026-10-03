# AuraAI Flask Responsive UI

This is a Flask-based responsive UI implementation matching the AuraAI dashboard reference.

## Run locally

1. Install dependencies:
   `pip install -r requirements.txt`
2. Start:
   `python flask_app.py`
3. Open:
   `http://127.0.0.1:5000`

The Flask UI is a frontend shell. Its navigation, quick-action buttons, recent-chat buttons, mobile drawer, and chat composer are interactive. Connect the buttons to the existing AuraAI backend/API when the Flask migration is ready.

The header intentionally keeps the AuraAI logo, divider, and **AI Career & Skills Navigator** tagline on the same desktop line, matching the supplied dashboard reference. On phones the tagline hides to preserve the compact header.
