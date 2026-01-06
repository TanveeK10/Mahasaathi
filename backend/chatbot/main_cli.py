#!/usr/bin/env python3
# backend/chatbot/main_cli.py
"""
CLI test harness for MahaSaathi chatbot with intent-based routing.

Usage:
    python main_cli.py              # Start CLI chat
    python main_cli.py --ingest     # Rebuild RAG DB first, then start chat

Features:
- Prompts for user_uid (or uses "anonymous")
- Calls chat_engine.chat_step() for each query
- Displays debug output: intent detection, params, DB queries, LLM responses
- Continuous conversation loop until user types "exit"
"""

import sys
import argparse
from chat_engine import chat_step
from rag_engine import ingest_documents
from config import APP_NAME, DEBUG

def main():
    parser = argparse.ArgumentParser(description="MahaSaathi CLI Test Harness")
    parser.add_argument(
        "--ingest",
        action="store_true",
        help="Rebuild RAG vector database before starting chat"
    )
    args = parser.parse_args()

    print("=" * 70)
    print(f"  {APP_NAME}")
    print("=" * 70)
    print()

    # Optional: Rebuild RAG database
    if args.ingest:
        print("🔄 Rebuilding RAG vector database...")
        try:
            ingest_documents()
            print("✅ RAG ingestion complete!\n")
        except Exception as e:
            print(f"❌ RAG ingestion failed: {e}")
            print("Continuing without RAG rebuild...\n")

    # Prompt for user_uid
    print("👤 Enter your user UID (or press Enter for 'anonymous'):")
    user_uid = input("   User UID: ").strip()
    if not user_uid:
        user_uid = "anonymous"
    
    print(f"\n✅ Logged in as: {user_uid}")
    print("\n💬 Type your questions below. Type 'exit' or 'quit' to end the session.\n")
    print("-" * 70)

    # Main chat loop
    while True:
        try:
            # Get user input
            user_query = input("\n🧑 You: ").strip()
            
            if not user_query:
                continue
            
            # Check for exit commands
            if user_query.lower() in ("exit", "quit", "bye"):
                print("\n👋 Goodbye! Thank you for using MahaSaathi.\n")
                break
            
            # Process query through chat engine
            print()
            print("=" * 70)
            
            # Get response (now returns a dict)
            response = chat_step(user_uid, user_query, debug=DEBUG)
            reply = response["reply"]
            
            print("=" * 70)
            print(f"\n🤖 MahaSaathi: {reply}")
            print()
            
        except KeyboardInterrupt:
            print("\n\n👋 Session interrupted. Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            if DEBUG:
                import traceback
                traceback.print_exc()
            print()

if __name__ == "__main__":
    main()
