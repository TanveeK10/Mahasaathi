import sys
import os

# Ensure chatbot module is in path
sys.path.append(os.path.join(os.path.dirname(__file__), "chatbot"))

from chat_engine import chat_step

# Mock user UID
USER_UID = "test_user_001"

print(f"Testing findNearest with Firebase Zone for user: {USER_UID}")
query = "Where is the nearest food?"
print(f"Query: {query}")

# Note: This test assumes the user exists in Firebase and has a 'zone' field.
# If not, it will fall back to Postgres or default.
# We are checking if the code runs without error.

try:
    response = chat_step(USER_UID, query, debug=True)
    print("\nResponse:")
    print(response["reply"])
    print("Intent Data:", response.get("intent_data"))
except Exception as e:
    print(f"\n❌ Error: {e}")
