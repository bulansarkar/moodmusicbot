"""
Mood-to-Music Backend API
FastAPI application for mood analysis and song recommendations
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
import logging

from app.models.schemas import (
    MoodRequest, 
    MoodAnalysisResponse, 
    HealthCheckResponse,
    MoodCategory
)
from app.utils.sentiment_analyzer import sentiment_analyzer
from app.utils.recommendation_engine import recommendation_engine

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Mood-to-Music API",
    description="AI-powered mood analysis and song recommendation engine",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API information"""
    return {
        "message": "Welcome to Mood-to-Music API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "redoc": "/api/redoc"
    }


@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return HealthCheckResponse(
        status="healthy",
        version="1.0.0",
        message="Mood-to-Music API is running successfully"
    )


@app.post("/api/analyze-mood", response_model=MoodAnalysisResponse, tags=["Mood Analysis"])
async def analyze_mood(request: MoodRequest):
    """
    Analyze user's mood and get song recommendations
    
    This endpoint:
    1. Analyzes the user's input using AI sentiment analysis
    2. Detects the mood category (very_sad, sad, anxious, neutral, happy, very_happy)
    3. Generates a mood score (0-10)
    4. Recommends 5 uplifting songs based on the detected mood
    
    Args:
        request: MoodRequest containing user's mood description
        
    Returns:
        MoodAnalysisResponse with detected mood, score, explanation, and song recommendations
    """
    try:
        # Validate input
        if not request.user_input or len(request.user_input.strip()) < 5:
            raise HTTPException(
                status_code=400,
                detail="Please provide a more detailed description of your mood (at least 5 characters)"
            )
        
        logger.info(f"Analyzing mood for input: {request.user_input[:50]}...")
        
        # Analyze sentiment
        detected_mood, mood_score, explanation = sentiment_analyzer.analyze_mood(
            request.user_input
        )
        
        logger.info(f"Detected mood: {detected_mood}, Score: {mood_score}")
        
        # Get song recommendations
        recommendations = recommendation_engine.get_recommendations(
            mood=detected_mood,
            count=5
        )
        
        logger.info(f"Generated {len(recommendations)} recommendations")
        
        # Create response
        response = MoodAnalysisResponse(
            detected_mood=detected_mood,
            mood_score=mood_score,
            sentiment_explanation=explanation,
            recommendations=recommendations
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing mood: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing mood: {str(e)}"
        )


@app.get("/api/moods", tags=["Mood Analysis"])
async def get_all_moods():
    """
    Get all available mood categories with descriptions
    
    Returns:
        Dictionary of mood categories and their descriptions
    """
    try:
        moods = recommendation_engine.get_all_moods()
        return {
            "moods": moods,
            "total": len(moods)
        }
    except Exception as e:
        logger.error(f"Error fetching moods: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching moods: {str(e)}"
        )


@app.get("/api/recommendations/{mood}", tags=["Recommendations"])
async def get_recommendations_by_mood(mood: str, count: int = 5):
    """
    Get song recommendations for a specific mood
    
    Args:
        mood: Mood category (very_sad, sad, anxious, neutral, happy, very_happy)
        count: Number of recommendations (default: 5)
        
    Returns:
        List of song recommendations
    """
    try:
        # Validate mood
        try:
            mood_category = MoodCategory(mood)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid mood. Valid moods are: {', '.join([m.value for m in MoodCategory])}"
            )
        
        # Validate count
        if count < 1 or count > 10:
            raise HTTPException(
                status_code=400,
                detail="Count must be between 1 and 10"
            )
        
        recommendations = recommendation_engine.get_recommendations(
            mood=mood_category,
            count=count
        )
        
        return {
            "mood": mood,
            "recommendations": recommendations,
            "count": len(recommendations)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting recommendations: {str(e)}"
        )


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "detail": exc.detail
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "status_code": 500,
            "detail": "Internal server error"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "True") == "True"
    )
