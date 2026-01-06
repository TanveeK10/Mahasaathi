import firebase_admin
from firebase_admin import credentials, firestore
import os
from typing import Optional, Tuple

# Global singleton for Firestore client
_db = None

def _init_firebase():
    global _db
    if _db is not None:
        return

    # Path to credentials file (backend/firebase_credentials.json)
    # This file is in backend/chatbot/, so we go up one level
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cred_path = os.path.join(base_dir, "firebase_credentials.json")

    if not os.path.exists(cred_path):
        print(f"[Firebase] ❌ Credentials not found at: {cred_path}")
        return

    try:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        _db = firestore.client()
        print("[Firebase] ✅ Connected to Firestore")
    except Exception as e:
        # If app already initialized, just get client
        try:
            _db = firestore.client()
        except:
            print(f"[Firebase] ❌ Initialization failed: {e}")

def get_user_zone(user_uid: str) -> Optional[int]:
    """
    Fetches the user's current zone ID from Firestore.
    Returns zone ID (int) or None if not found/error.
    """
    _init_firebase()
    if _db is None:
        return None

    try:
        doc_ref = _db.collection("users").document(user_uid)
        doc = doc_ref.get()

        if doc.exists:
            data = doc.to_dict()
            # Assuming field is 'zone' or 'current_zone'
            # Based on previous context, user said "zone of the user"
            # I'll check for 'zone' first, then 'last_seen_zone'
            zone = data.get("zone") or data.get("last_seen_zone")
            
            if zone is not None:
                return int(zone)
    except Exception as e:
        print(f"[Firebase] Error fetching zone for {user_uid}: {e}")
    
    return None
