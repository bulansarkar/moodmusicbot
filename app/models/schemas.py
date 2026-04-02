"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class MoodCategory(str, Enum):
    """Mood categories detected by sentiment analysis"""
    VERY_SAD = "very_sad"
    SAD = "sad"
    ANXIOUS = "anxious"
    NEUTRAL = "neutral"
    HAPPY = "happy"
    VERY_HAPPY = "very_happy"


class MoodRequest(BaseModel):
    """Request model for mood input"""
    user_input: str = Field(..., min_length=5, max_length=1000, description="User's description of their mood/feelings")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_input": "I've been feeling really down lately, nothing seems to interest me anymore"
            }
        }


class SongRecommendation(BaseModel):
    """Model for a single song recommendation"""
    title: str = Field(..., description="Song title")
    artist: str = Field(..., description="Artist name")
    youtube_id: str = Field(..., description="YouTube video ID for embedding")
    reason: str = Field(..., description="Why this song is recommended for the detected mood")
    youtube_url: str = Field(..., description="Full YouTube URL")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Walking on Sunshine",
                "artist": "Katrina & The Waves",
                "youtube_id": "iPUmE-tne5U",
                "reason": "Uplifting and energetic song perfect for boosting mood",
                "youtube_url": "https://www.youtube.com/watch?v=iPUmE-tne5U"
            }
        }


class MoodAnalysisResponse(BaseModel):
    """Response model for mood analysis"""
    detected_mood: MoodCategory = Field(..., description="Detected mood category")
    mood_score: float = Field(..., ge=0, le=10, description="Mood score from 0 (very sad) to 10 (very happy)")
    sentiment_explanation: str = Field(..., description="AI explanation of detected sentiment")
    recommendations: List[SongRecommendation] = Field(..., description="List of recommended songs")
    
    class Config:
        json_schema_extra = {
            "example": {
                "detected_mood": "sad",
                "mood_score": 3.5,
                "sentiment_explanation": "The user expresses feelings of depression and lack of interest, indicating a sad mood state.",
                "recommendations": [
                    {
                        "title": "Walking on Sunshine",
                        "artist": "Katrina & The Waves",
                        "youtube_id": "iPUmE-tne5U",
                        "reason": "Uplifting and energetic song perfect for boosting mood",
                        "youtube_url": "https://www.youtube.com/watch?v=iPUmE-tne5U"
                    }
                ]
            }
        }


class HealthCheckResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(..., description="API status")
    version: str = Field(..., description="API version")
    message: str = Field(..., description="Status message")
