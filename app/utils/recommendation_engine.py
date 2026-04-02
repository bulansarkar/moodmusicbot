"""
Song Recommendation Engine
Recommends songs based on detected mood
"""
import json
import os
import random
from typing import List, Dict, Any
from app.models.schemas import MoodCategory, SongRecommendation


class RecommendationEngine:
    """Recommends songs based on mood category"""
    
    def __init__(self):
        """Load songs database"""
        self.songs_db = self._load_songs_database()
    
    def _load_songs_database(self) -> Dict[str, Any]:
        """Load the songs database from JSON file"""
        db_path = os.path.join(os.path.dirname(__file__), "../../data/songs_database.json")
        
        try:
            with open(db_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Songs database not found at {db_path}")
            return {}
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON in songs database")
            return {}
    
    def get_recommendations(self, mood: MoodCategory, count: int = 5) -> List[SongRecommendation]:
        """
        Get song recommendations for a given mood
        
        Args:
            mood: Detected mood category
            count: Number of recommendations to return
            
        Returns:
            List of SongRecommendation objects
        """
        mood_key = mood.value
        
        if mood_key not in self.songs_db:
            # Fallback to neutral if mood not found
            mood_key = "neutral"
        
        mood_data = self.songs_db.get(mood_key, {})
        songs = mood_data.get("songs", [])
        
        if not songs:
            return []
        
        # Shuffle and select top N songs
        shuffled_songs = random.sample(songs, min(count, len(songs)))
        
        recommendations = []
        for song in shuffled_songs:
            recommendation = SongRecommendation(
                title=song.get("title", "Unknown"),
                artist=song.get("artist", "Unknown"),
                youtube_id=song.get("youtube_id", ""),
                reason=song.get("reason", ""),
                youtube_url=f"https://www.youtube.com/watch?v={song.get('youtube_id', '')}"
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    def get_all_moods(self) -> Dict[str, str]:
        """Get all available mood categories with descriptions"""
        moods = {}
        for mood_key, mood_data in self.songs_db.items():
            moods[mood_key] = mood_data.get("description", "")
        return moods


# Initialize global recommendation engine instance
recommendation_engine = RecommendationEngine()
