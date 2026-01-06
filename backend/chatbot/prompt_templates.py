# backend/prompt_templates.py

CHAT_TEMPLATE = """You are MahaSaathi, a helpful assistant for Pune Ganeshotsav festival.

CRITICAL RULES:
1. Answer in the SAME language as the user's question (English→English, Marathi→Marathi, Hindi→Hindi)
2. Be concise and helpful
3. Only use information provided in <context> or <intent_data>
4. If you don't have the information, say: "माझ्याकडे याबाबतची माहिती उपलब्ध नाही."
5. Never invent facts or make up information

When <intent_data> is provided:
- Use ONLY the data in <intent_data>
- Rewrite it naturally in the user's language
- Keep it short and clear

When <context> is provided:
- Use ONLY information from <context>
- Answer the user's question based on context
- If answer not in context, use the fallback message above
"""


def build_prompt(user_query: str,
                 retrieved_chunks=None,
                 intent_data: dict = None) -> str:
    """
    Builds the final prompt for the LLM.

    CASE 1 → RAG MODE:
        retrieved_chunks = list of context texts
        intent_data = None

    CASE 2 → INTENT MODE:
        retrieved_chunks = None
        intent_data = dict with processed real-time data

    Parameters
    ----------
    user_query : str
        The user's question.
    retrieved_chunks : list[str] or None
        Chunks from vector search (RAG mode only)
    intent_data : dict or None
        Real-time factual data from intent handlers (intent mode only)

    Returns
    -------
    str : final prompt string for the LLM
    """

    # ---------------------------
    # Case 1 — RAG MODE
    # ---------------------------
    if intent_data is None and retrieved_chunks:
        context_block = "\n\n".join(retrieved_chunks)
        return f"""
{CHAT_TEMPLATE}

<context>
{context_block}
</context>

User query:
{user_query}

Using ONLY <context>, give the best factual answer.
"""

    # ---------------------------
    # Case 2 — INTENT MODE
    # ---------------------------
    if intent_data is not None:
        # Convert dict to a readable block
        pretty_intent_data = "\n".join(
            f"{k}: {v}" for k, v in intent_data.items()
        )

        return f"""You are MahaSaathi, a helpful assistant for Pune Ganeshotsav.

<intent_data>
{pretty_intent_data}
</intent_data>

User asked: {user_query}

Using ONLY the information in <intent_data>, provide a helpful answer in the SAME language as the user's question.
Be concise and natural.
IMPORTANT:
- Do NOT invent any information.
- Keep place names (like "Sarasbaug", "Dagdusheth") exactly as they are (or transliterate accurately).
- Keep numbers (distances) exactly as provided."""

    # ---------------------------
    # Safety fallback (should never happen)
    # ---------------------------
    return f"""
{CHAT_TEMPLATE}

User query:
{user_query}

No context or intent data was provided. Reply:
"माझ्याकडे याबाबतची माहिती उपलब्ध नाही."
"""
