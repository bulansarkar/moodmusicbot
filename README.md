# Mood-to-Music Backend API

A Python FastAPI backend for a college project that analyzes user mood using AI sentiment analysis and recommends uplifting YouTube songs.

## Features

- **AI Sentiment Analysis**: Uses OpenAI API (with a keyword-based fallback) to detect 6 mood categories: `very_sad`, `sad`, `anxious`, `neutral`, `happy`, `very_happy`.
- **Song Recommendation Engine**: Curated database of songs mapped to specific moods.
- **FastAPI Framework**: Modern, fast, and auto-documented API.
- **CORS Configured**: Ready to connect with a React frontend.

## Project Structure

```
mood-music-backend/
├── app/
│   ├── models/
│   │   └── schemas.py          # Pydantic models for request/response validation
│   ├── utils/
│   │   ├── sentiment_analyzer.py   # AI mood detection logic
│   │   └── recommendation_engine.py # Song recommendation logic
│   └── main.py                 # FastAPI application and endpoints
├── data/
│   └── songs_database.json     # Curated mood-to-song mapping
├── .env                        # Environment variables
└── requirements.txt            # Python dependencies
```

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key to the `.env` file (optional, the app has a fallback mechanism if no key is provided)

3. **Run the Server**:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

4. **View API Documentation**:
   - Open your browser and navigate to `http://localhost:8000/api/docs` to see the interactive Swagger UI.

## API Endpoints

- `GET /health`: Check API status
- `GET /api/moods`: Get all available mood categories
- `POST /api/analyze-mood`: Submit text to get mood analysis and song recommendations
- `GET /api/recommendations/{mood}`: Get song recommendations for a specific mood

## Next Steps for Frontend

When building the React frontend, you can use `axios` or `fetch` to call the `/api/analyze-mood` endpoint:

```javascript
const response = await fetch('http://localhost:8000/api/analyze-mood', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ user_input: "I'm feeling a bit down today..." })
});
const data = await response.json();
// Use data.recommendations to display YouTube embeds
```
