# backend/intent_engine.py
"""
Hybrid intent detection:
1) Quick keyword-based rules to propose intent + params
2) Optional Ollama validation prompt that confirms/refines the detected intent
Returns: dict with keys: intent, params (dict), confidence (float), explanation (str)
"""

from typing import Dict, Tuple, Optional
import re
from ollama_client import query_ollama
from config import LLM_MODEL, DEBUG

# Basic keyword map for rule-based detection
KEYWORD_INTENT_MAP = {
    "nearest": "findNearest",
    "nearest to me": "findNearest",
    "where is": "findNearest",
    "where are": "findNearest",
    "direction": "getDirections",
    "directions": "getDirections",
    "how to get": "getDirections",
    "crowd": "checkCrowd",
    "crowded": "checkCrowd",
    "security": "showSecurity",
    "police": "showSecurity",
    "booth": "showSecurity",
    "nearest metro": "findNearest",
    "metro": "findNearest",
    "toilet": "findNearest",
    "washroom": "findNearest",
    "food": "findNearest",
    "medical": "findNearest",
    # Marathi/Hindi keywords
    "kuthe aahe": "findNearest",  # Marathi
    "kahan hai": "findNearest",   # Hindi
    "kidhar hai": "findNearest",  # Hindi
    "jawalche": "findNearest",    # Marathi (nearest)
    "pass wala": "findNearest",   # Hindi (nearest)
    "gardi": "checkCrowd",        # Marathi (crowd)
    "bheed": "checkCrowd",        # Hindi (crowd)
    "rasta": "getDirections",     # Marathi/Hindi (route)
    "marg": "getDirections",      # Marathi/Hindi (route)
    "police": "showSecurity",
    "suraksha": "showSecurity",   # Marathi/Hindi (security)
}

def _rule_detect(query: str) -> Tuple[Optional[str], Dict]:
    q = query.lower()
    
    # Category extraction (Multilingual)
    # Washroom
    if any(w in q for w in ["toilet", "washroom", "shauchalay", "sandas", "bathroom", "शौचालय", "बाथरूम"]):
        return "findNearest", {"category": "washroom"}
    
    # Commutation
    if any(w in q for w in ["metro", "station", "bus", "stop", "rickshaw", "auto", "मेट्रो", "बस", "रिक्षा", "स्टेशन"]):
        return "findNearest", {"category": "commutation"}
    
    # Food
    if any(w in q for w in ["food", "snack", "restaurant", "hotel", "khana", "jevan", "nashta", "vada pav", "जेवण", "खाणे", "नाश्ता", "वडापाव", "हॉटेल"]):
        return "findNearest", {"category": "food"}
    
    # Medical
    if any(w in q for w in ["medical", "hospital", "clinic", "dawakhana", "doctor", "दवाखाना", "हॉस्पिटल", "डॉक्टर"]):
        return "findNearest", {"category": "medical"}
    
    # Security
    if any(w in q for w in ["police", "security", "booth", "chowki", "police station", "पोलीस", "सुरक्षा", "चौकी"]):
        return "showSecurity", {}
    
    # Crowd
    if any(w in q for w in ["crowd", "crowded", "busy", "how many people", "gardi", "bheed", "log", "गर्दी", "भीड", "लोक"]):
        return "checkCrowd", {}
    
    # Directions
    if any(w in q for w in ["direction", "directions", "how to get", "how to reach", "route", "rasta", "marg", "jane ka", "jaycha", "रस्ता", "मार्ग", "कसे जायचे", "जायचे"]):
        # try to extract target location name
        # naive extraction: words after "to" or "towards" or "kade"
        m = re.search(r"(?:to|towards|reach|kade|taraf|la) (.+)", q)
        target = m.group(1) if m else None
        return "getDirections", {"target": target}
        
    # fallback: keyword map
    for k, intent in KEYWORD_INTENT_MAP.items():
        if k in q:
            return intent, {}
    return None, {}

def detect_intent(query: str, validate_with_llm: bool = True) -> Dict:
    """
    Return a dict:
    {
        "intent": "findNearest" | "getDirections" | "checkCrowd" | "showSecurity" | "fallback",
        "params": {...},
        "confidence": float,
        "explanation": str
    }
    """
    intent, params = _rule_detect(query)
    explanation = "Detected by rules."

    # If rules couldn't detect anything, fallback to asking Ollama to classify
    if intent is None and validate_with_llm:
        # Ask Ollama to label intent succinctly (very short prompt)
        system = "You are an intent classifier. Return only intent name: one of findNearest, getDirections, checkCrowd, showSecurity, or fallback."
        user = f"Classify the intent of this user query (one word):\n\n\"{query}\""
        llm_resp = query_ollama(system, user, model=LLM_MODEL)
        resp = llm_resp.strip().splitlines()[0].strip()
        if resp in ("findNearest", "getDirections", "checkCrowd", "showSecurity"):
            intent = resp
            params = {}
            explanation = "Detected by LLM classification."
        else:
            intent = "fallback"
            explanation = f"LLM returned: {resp}"

    # If rules detected something and we want LLM validation, optionally confirm
    confidence = 0.9 if intent and intent != "fallback" else 0.0
    if validate_with_llm and intent and intent != "fallback":
        # small validation prompt: confirm the intent, nothing fancy
        system = "You are a classifier that answers with JSON: {\"intent\":\"...\", \"confidence\":0.0, \"explain\":\"...\"}"
        user = f"User query: \"{query}\"\nDetected intent (from rules): {intent}\nReturn JSON only, confirming or correcting the intent and confidence (0-1)."
        try:
            llm_resp = query_ollama(system, user, model=LLM_MODEL)
            # try to parse simple json-ish response safely: naive parse
            import json
            try:
                parsed = json.loads(llm_resp.strip())
                intent = parsed.get("intent", intent)
                confidence = float(parsed.get("confidence", confidence))
                explanation = parsed.get("explain", explanation)
            except Exception:
                # If LLM didn't return valid JSON, keep rule-based decision
                explanation = explanation + " (LLM validation didn't return JSON)"
        except Exception as e:
            explanation = explanation + f" (LLM validation error: {e})"

    return {
        "intent": intent if intent else "fallback",
        "params": params,
        "confidence": float(confidence),
        "explanation": explanation
    }
