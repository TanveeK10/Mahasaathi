# MahaSaathi - Pune Ganeshotsav Assistant

MahaSaathi is an intelligent assistant for Pune Ganeshotsav that combines RAG (Retrieval-Augmented Generation) with real-time RFID tracking to answer festival-related questions in Marathi, Hindi, and English.

## Features

- **Dual-Mode Operation**:
  - **RAG Mode**: Answers factual questions from document knowledge base
  - **Intent Mode**: Handles real-time queries (nearest facilities, crowd levels, directions, security)
- **Language-Aware**: Responds in the same language as the query (Marathi/Hindi/English)
- **No Hallucinations**: Only uses verified context or real-time data
- **RFID Integration**: Tracks user location and crowd density across festival zones
- **Ollama** with `gemma2:9b` model:
   ```bash
   # Install Ollama from https://ollama.ai
   ollama pull gemma2:9b
   ```

## Installation

### 1. Clone and Setup Environment

```bash
git clone https://github.com/TanveeK10/Mahasaathi.git
cd Mahasaathi/backend

# Create virtual environment (optional but recommended)
python -m venv .venv
.venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the `backend/` directory. You can use the following template:

```bash
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=Mahasaathi_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password_here
PG_DSN=postgresql://postgres:your_password_here@localhost:5432/Mahasaathi_db
OLLAMA_URL=http://localhost:11434
```

### 3. Verify Database

Your database is already set up with 100 locations. Let's verify the connection:

```bash
# Verify database structure and data
cd database
python verify_db.py
```

### 4. Build RAG Vector Database

To enable the chatbot to answer questions about the festival, build the knowledge base:

```bash
cd ../chatbot
python rag_ingest.py
```

## Usage

### CLI Testing

You can test the chatbot directly in your terminal:

```bash
cd chatbot
python main_cli.py
```

**Sample Session:**
```
🧑 You: Where is the nearest washroom?
🤖 MahaSaathi: The nearest washroom is at Dagdusheth Area, approximately 150 meters away.
```

### FastAPI Server

To run the backend API server:

```bash
cd backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
Mahasaathi/
├── README.md              # Project documentation
├── backend/
│   ├── .env               # Environment configuration
│   ├── requirements.txt   # Python dependencies
│   ├── app.py             # FastAPI application
│   ├── chatbot/           # Chatbot logic & RAG engine
│   ├── database/          # Database scripts & schema
│   ├── rag_docs/          # Knowledge base documents
│   └── chroma_db/         # ChromaDB persistent storage
```

## Intents & Algorithms

1. **findNearest(category)**: Queries database using Haversine distance.
2. **getDirections(target)**: Uses RAG to find navigation/walking route context.
3. **checkCrowd()**: Analyzes recent RFID scans to determine crowd density.
4. **showSecurity()**: Locates nearest police/security booths.

## License

This project is developed for educational purposes as part of the EDAI_V course.
