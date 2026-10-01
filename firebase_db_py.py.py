import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
import json

# Your exact Firebase Web Configuration
firebase_config = {
    "apiKey": "AIzaSyDquk8cNPkQ2onzVlgzhriwm_LS8jHMdhY",
    "authDomain": "learningaccelerator-61452.firebaseapp.com",
    "projectId": "learningaccelerator-61452",
    "storageBucket": "learningaccelerator-61452.firebasestorage.app",
    "messagingSenderId": "700119982345",
    "appId": "1:700119982345:web:b170ac89d94a29924cb3d8",
    "databaseURL": ""
}

# Initialize Pyrebase for User Authentication (Signup / Login)
try:
    firebase = pyrebase.initialize_app(firebase_config)
    auth = firebase.auth()
except Exception as e:
    auth = None

# Initialize Firebase Admin for Firestore Database operations SECURELY
if not firebase_admin._apps:
    try:
        # 1. Try to load from Streamlit Secrets (Best for Cloud Deployment)
        if "firebase" in st.secrets:
            cred_dict = dict(st.secrets["firebase"])
            # If the private key was stored as a string, parse it back to a dict
            if isinstance(cred_dict.get("private_key"), str):
                cred_dict = json.loads(cred_dict["private_key"])
            cred = credentials.Certificate(cred_dict)
        # 2. Fallback to local JSON file (ONLY for local development - DO NOT COMMIT)
        else:
            cred = credentials.Certificate("firebase_credentials.json")
            
        firebase_admin.initialize_app(cred)
    except Exception as e:
        print(f"Firebase Admin Initialization Error: {e}")

# Safely initialize the database client
db = firestore.client() if firebase_admin._apps else None

# --- Core Database & Auth Functions ---
# ... (rest of your functions remain the same) ...