# backend/chat_engine.py
"""
Master chat engine for CLI testing with updated dual-mode prompting.

- Detects intent (hybrid: rules + LLM validation)
- Collects real-time data from PostgreSQL for intents
- Creates intent_data dict
- For RAG mode -> uses vector search chunks
- For INTENT mode -> ignores RAG and uses only intent_data
- Uses updated build_prompt() from prompt_templates.py
"""

from typing import Dict, Optional
from intent_engine import detect_intent
from rag_engine import search as rag_search
from ollama_client import query_ollama
from db import (
    get_user_latest_zone,
    get_locations_by_category,
    get_recent_scan_count,
    get_security_locations,
    get_zone_center
)
from firebase_client import get_user_zone
from prompt_templates import CHAT_TEMPLATE, build_prompt
from config import LLM_MODEL, RAG_TOP_K, DEBUG, MAX_HISTORY
import math

# ====================================================
# Utility: Haversine distance
# ====================================================
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dl/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c


# ====================================================
# INTENT HANDLERS - return INTENT_DATA dict
# ====================================================

def handle_find_nearest(user_uid: str, params: Dict) -> Dict:
    """
    Returns intent_data for nearest location:
    {
        "name": <place>,
        "distance_m": <int>,
        "category": <category>
    }
    """
    category = params.get("category")
    if not category:
        return {"error": "category_missing"}

    candidates = get_locations_by_category(category)
    if not candidates:
        return {"error": "no_locations"}

    # determine user approximate center
    # 1. Try Firebase (Zone ID)
    fb_zone = get_user_zone(user_uid)
    
    user_lat = None
    user_lon = None

    if fb_zone is not None:
        # Get coords for this zone from Postgres
        center = get_zone_center(fb_zone)
        if center:
            user_lat, user_lon = center
    
    # 2. Fallback to Postgres (Last Seen Zone) if Firebase didn't help
    if user_lat is None:
        pg_zone = get_user_latest_zone(user_uid)
        if pg_zone is not None:
            center = get_zone_center(pg_zone)
            if center:
                user_lat, user_lon = center
    
    # If still no location (unknown user or invalid zone), use Dagdusheth as default
    if user_lat is None:
        # Default: Dagdusheth Halwai Ganpati Pandal
        user_lat = 18.5158
        user_lon = 73.8567

    # compute nearest
    scored = []
    for c in candidates:
        d = haversine(user_lat, user_lon, c["latitude"], c["longitude"])
        scored.append((d, c))
    scored.sort(key=lambda x: x[0])

    nearest = scored[0][1]
    distance = int(scored[0][0])

    return {
        "mode": "findNearest",
        "name": nearest["name"],
        "distance_m": distance,
        "category": category,
    }


def handle_get_directions(user_uid: str, params: Dict, user_query: str) -> Dict:
    """
    Uses RAG to extract related info + LLM to rewrite.
    We do NOT compute real map routes (future feature).
    """
    target = params.get("target")
    if not target:
        return {"error": "target_missing"}

    docs = rag_search(target, k=RAG_TOP_K)
    if not docs:
        return {"error": "no_context"}

    context_texts = [d["document"] for d in docs]

    return {
        "mode": "getDirections",
        "target": target,
        "context_snippets": context_texts
    }


def handle_check_crowd(user_uid: str) -> Dict:
    """
    Weighted density mode: C
    {
        "mode": "checkCrowd",
        "zone": <zone>,
        "count_5min": <int>,
        "level": "LOW"|"MEDIUM"|"HIGH"
    }
    """
    zone = get_user_latest_zone(user_uid)
    if zone is None:
        return {"error": "zone_unknown"}

    count = get_recent_scan_count(zone, minutes=5)

    if count <= 10:
        level = "LOW"
    elif count <= 30:
        level = "MEDIUM"
    else:
        level = "HIGH"

    return {
        "mode": "checkCrowd",
        "zone": zone,
        "count_5min": count,
        "level": level,
    }


def handle_show_security(user_uid: str) -> Dict:
    """
    Returns:
    {
        "mode": "showSecurity",
        "name": nearest_security_place,
        "distance_m": <int>
    }
    """
    candidates = get_security_locations()
    if not candidates:
        return {"error": "no_security"}

    # determine user approximate center
    # 1. Try Firebase (Zone ID)
    fb_zone = get_user_zone(user_uid)
    
    user_lat = None
    user_lon = None

    if fb_zone is not None:
        center = get_zone_center(fb_zone)
        if center:
            user_lat, user_lon = center

    # 2. Fallback to Postgres
    if user_lat is None:
        pg_zone = get_user_latest_zone(user_uid)
        if pg_zone is not None:
            center = get_zone_center(pg_zone)
            if center:
                user_lat, user_lon = center
    
    # If still no location, use Dagdusheth
    if user_lat is None:
        user_lat = 18.5158
        user_lon = 73.8567

    scored = []
    for c in candidates:
        d = haversine(user_lat, user_lon, c["latitude"], c["longitude"])
        scored.append((d, c))
    scored.sort(key=lambda x: x[0])

    best = scored[0][1]
    distance = int(scored[0][0])

    return {
        "mode": "showSecurity",
        "name": best["name"],
        "distance_m": distance
    }


# ====================================================
# CHAT ORCHESTRATOR - routes intents + builds prompt
# ====================================================

history = []


def chat_step(user_uid: str, user_query: str, debug: bool = True) -> Dict:
    """
    Single turn of conversation.
    - Detect intent
    - If intent found -> build INTENT_DATA prompt
    - Else -> fallback to RAG mode
    """

    # Maintain simple in-memory chat history
    history.append({"role": "user", "content": user_query})
    if len(history) > MAX_HISTORY * 2:
        history[:] = history[-MAX_HISTORY*2:]


    # 1) Detect intent
    intent_res = detect_intent(user_query)
    intent = intent_res["intent"]
    params = intent_res["params"]

    if debug:
        print(f"\n[DEBUG] Intent = {intent}")
        print(f"[DEBUG] Params = {params}")
        print(f"[DEBUG] Explanation = {intent_res['explanation']}\n")


    # 2) INTENT MODE — handle real-time queries
    if intent == "findNearest":
        intent_data = handle_find_nearest(user_uid, params)

    elif intent == "getDirections":
        intent_data = handle_get_directions(user_uid, params, user_query)

    elif intent == "checkCrowd":
        intent_data = handle_check_crowd(user_uid)

    elif intent == "showSecurity":
        intent_data = handle_show_security(user_uid)

    else:
        intent_data = None  # triggers RAG mode


    # If INTENT_DATA contains an error -> fallback to RAG
    if intent_data and "error" in intent_data:
        if debug:
            print(f"[DEBUG] Intent handler error -> {intent_data['error']}")
        intent_data = None


    # 3 ) MODE SELECTION
    if intent_data:
        # INTENT MODE
        prompt = build_prompt(
            user_query=user_query,
            intent_data=intent_data
        )
        reply = query_ollama(CHAT_TEMPLATE, prompt, model=LLM_MODEL)

    else:
        # RAG MODE (fallback factual answers)
        docs = rag_search(user_query, k=RAG_TOP_K)

        if not docs:
            reply = "I dont know. Sorry"
        else:
            context_texts = [d["document"] for d in docs]
            prompt = build_prompt(
                user_query=user_query,
                retrieved_chunks=context_texts
            )
            reply = query_ollama(CHAT_TEMPLATE, prompt, model=LLM_MODEL)


    history.append({"role": "assistant", "content": reply})
    history.append({"role": "assistant", "content": reply})
    
    # Return structured response
    return {
        "reply": reply,
        "intent": intent,
        "intent_data": intent_data,
        "params": params
    }
