# MahaSaathi - Pune Ganeshotsav Assistant

MahaSaathi is an intelligent assistant for Pune Ganeshotsav that combines RAG (Retrieval-Augmented Generation) with real-time RFID tracking to answer festival-related questions in Marathi, Hindi, and English.

## Features

- **Dual-Mode Operation**:
  - **RAG Mode**: Answers factual questions from document knowledge base
  - **Intent Mode**: Handles real-time queries (nearest facilities, crowd levels, directions, security)
- **Language-Aware**: Responds in the same language as the query (Marathi/Hindi/English)
- **No Hallucinations**: Only uses verified context or real-time data
- **RFID Integration**: Tracks user location and crowd density across festival zones
- **Ollama** with `phi3:mini` model:
   ```bash
   # Install Ollama from https://ollama.ai
   ollama pull phi3:mini
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

The `.env` file is already configured. Verify the settings:

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

Your database is already set up with 100 locations. Let's verify the connection and optionally add test users:

```bash
# Verify database structure and data
cd database
python verify_db.py
```

**Expected Output:**
```
============================================================
MahaSaathi Database Verification
============================================================
🔌 Connecting to database...
✅ Database connection successful!
...
✅ Database verification complete!
============================================================
```

### 4. Build RAG Vector Database

```bash
cd ../chatbot
python rag_ingest.py
```

**Expected Output:**
```
[RAG] Ingested 6 chunks from 01_dagdusheth.md
...
✅ RAG ingestion done.
```

## Usage

### CLI Testing

```bash
cd chatbot
python main_cli.py --ingest  # Rebuild RAG DB first (optional)
```

**Sample Session:**
```
======================================================================
  MahaSaathi Assistant (CLI Test)
======================================================================
...
🧑 You: Where is the nearest washroom?
🤖 MahaSaathi: The nearest washroom is at Dagdusheth Area, approximately 150 meters away.
```

### Sample Queries

#### RAG Mode (Factual Questions)
- "When is the aarti at Dagdusheth?"
- "What is the history of Kasba Ganpati?"
- "Tell me about parking facilities"

#### Intent Mode (Real-time Queries)

**findNearest:**
- "Where is the nearest washroom?"
- "Nearest metro station?"

**getDirections:**
- "How to get to Shaniwarwada?"

**checkCrowd:**
- "Is it crowded right now?"

**showSecurity:**
- "Where is the police booth?"

#### Language Testing
- Marathi: "जवळचे शौचालय कुठे आहे?"
- Hindi: "निकटतम शौचालय कहाँ है?"
- English: "Where is the nearest washroom?"

## FastAPI Server

### Start Server

```bash
cd backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### API Endpoints

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Chat Endpoint
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_uid": "test_user_001",
    "query": "Where is the nearest washroom?"
  }'
```

### API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

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
└── ...
```

## Intents & Algorithms

### 1. findNearest(category)
- Queries `locations` table by category
- Computes distance using Haversine formula
- Returns nearest location name and distance in meters

### 2. getDirections(target)
- Uses RAG to find context about target location
- LLM rewrites context into step-by-step directions

### 3. checkCrowd()
- Counts RFID scans in last 5 minutes per zone
- Thresholds: ≤10 LOW, 11-30 MEDIUM, >30 HIGH

### 4. showSecurity()
- Queries `locations` table for category='security'

## Database Schema

- **locations**: Pandals, washrooms, food, commutation, medical, security
- **rfid_readers**: 6 readers across 3 zones (Entry, Inner Temple, Exit)
- **rfid_activity**: RFID scan logs with timestamps
- **users**: User tracking with last seen zone/reader

## Troubleshooting

### Database Connection Error
**Solution:** Verify `.env` file exists and `PG_DSN` is correctly set.

### Ollama Not Running
**Solution:** Start Ollama service and ensure `phi3:mini` model is installed.

### ChromaDB Collection Not Found
**Solution:** Run RAG ingestion.

## Future Enhancements

- [ ] User GPS integration for accurate distance calculation
- [ ] Real-time map routing with OSRM/Google Maps
- [ ] Chat history logging to database
- [ ] User profile personalization

## License

This project is developed for educational purposes as part of the EDAI_V course.

## Support

For issues or questions, please contact the development team.

---

**MahaSaathi** - Making Pune Ganeshotsav accessible and enjoyable for everyone! 🙏
