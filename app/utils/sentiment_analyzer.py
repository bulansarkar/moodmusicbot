"""
Sentiment Analysis Engine using OpenAI API
Analyzes user input to detect mood and emotional state
"""
import os
import json
from typing import Tuple, Dict, Any
from app.models.schemas import MoodCategory


class SentimentAnalyzer:
    """Analyzes user input to detect mood using OpenAI API"""
    
    def __init__(self):
        """Initialize OpenAI client"""
        api_key = os.getenv("OPENAI_API_KEY")
        
        # For testing/development without API key
        if not api_key or api_key == "your_openai_api_key_here":
            self.client = None
            self.use_fallback = True
            print("⚠️  Warning: OpenAI API key not configured. Using fallback sentiment analysis.")
        else:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=api_key)
                self.use_fallback = False
            except Exception as e:
                print(f"⚠️  Warning: Could not initialize OpenAI client: {e}. Using fallback analysis.")
                self.client = None
                self.use_fallback = True
        
        self.model = "gpt-4.1-mini"  # Using available model
        
    def analyze_mood(self, user_input: str) -> Tuple[MoodCategory, float, str]:
        """
        Analyze user input to detect mood and emotional state
        
        Args:
            user_input: User's description of their mood/feelings
            
        Returns:
            Tuple of (mood_category, mood_score, explanation)
        """
        if self.use_fallback or self.client is None:
            return self._fallback_sentiment_analysis(user_input)
        
        prompt = self._create_analysis_prompt(user_input)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert psychologist and mood analyzer. Analyze the user's input and detect their emotional state. Respond ONLY with valid JSON, no additional text."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Parse response
            response_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response (in case there's extra text)
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError:
                # Try to extract JSON from the response
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    raise ValueError("Could not parse AI response")
            
            # Validate and extract values
            mood = self._validate_mood_category(result.get("mood_category", "neutral"))
            score = float(result.get("mood_score", 5.0))
            explanation = result.get("explanation", "Mood analysis completed.")
            
            # Ensure score is within valid range
            score = max(0, min(10, score))
            
            return mood, score, explanation
            
        except Exception as e:
            print(f"Error in sentiment analysis: {str(e)}")
            # Fallback to keyword-based analysis
            return self._fallback_sentiment_analysis(user_input)
    
    def _fallback_sentiment_analysis(self, user_input: str) -> Tuple[MoodCategory, float, str]:
        """
        Fallback sentiment analysis using keyword matching
        Used when OpenAI API is not available
        """
        user_lower = user_input.lower()
        
        # Define keyword patterns for each mood
        very_sad_keywords = ['depressed', 'suicidal', 'hopeless', 'worthless', 'nothing matters', 'can\'t go on', 'give up', 'terrible', 'worst']
        sad_keywords = ['sad', 'down', 'disappointed', 'unhappy', 'blue', 'depressed', 'miserable', 'gloomy', 'sorry', 'regret']
        anxious_keywords = ['anxious', 'worried', 'stressed', 'nervous', 'overwhelmed', 'panic', 'afraid', 'scared', 'tense', 'uneasy']
        happy_keywords = ['happy', 'good', 'great', 'wonderful', 'excellent', 'love', 'enjoy', 'fun', 'grateful', 'blessed']
        very_happy_keywords = ['very happy', 'ecstatic', 'thrilled', 'excited', 'amazing', 'fantastic', 'perfect', 'incredible', 'joyful', 'euphoric']
        
        # Count keyword matches
        very_sad_count = sum(1 for keyword in very_sad_keywords if keyword in user_lower)
        sad_count = sum(1 for keyword in sad_keywords if keyword in user_lower)
        anxious_count = sum(1 for keyword in anxious_keywords if keyword in user_lower)
        happy_count = sum(1 for keyword in happy_keywords if keyword in user_lower)
        very_happy_count = sum(1 for keyword in very_happy_keywords if keyword in user_lower)
        
        # Determine mood based on keyword matches
        counts = {
            'very_sad': very_sad_count,
            'sad': sad_count,
            'anxious': anxious_count,
            'happy': happy_count,
            'very_happy': very_happy_count
        }
        
        # Find the mood with highest count
        max_mood = max(counts, key=counts.get)
        max_count = counts[max_mood]
        
        # If no strong match, default to neutral
        if max_count == 0:
            mood = MoodCategory.NEUTRAL
            score = 5.0
            explanation = "Neutral mood detected. No strong emotional indicators found."
        else:
            mood = MoodCategory(max_mood)
            
            # Calculate mood score based on keyword counts
            if max_mood == 'very_sad':
                score = 1.0 + (max_count * 0.5)
            elif max_mood == 'sad':
                score = 2.5 + (max_count * 0.5)
            elif max_mood == 'anxious':
                score = 4.0 + (max_count * 0.3)
            elif max_mood == 'happy':
                score = 6.5 + (max_count * 0.5)
            elif max_mood == 'very_happy':
                score = 8.5 + (max_count * 0.5)
            else:
                score = 5.0
            
            score = max(0, min(10, score))
            explanation = f"Detected {max_mood.replace('_', ' ')} mood based on emotional keywords in your input."
        
        return mood, score, explanation
    
    def _create_analysis_prompt(self, user_input: str) -> str:
        """Create a structured prompt for mood analysis"""
        return f"""Analyze the following user input and detect their emotional state. 
        
User Input: "{user_input}"

Respond with ONLY a JSON object (no markdown, no extra text) with these exact fields:
{{
    "mood_category": "one of: very_sad, sad, anxious, neutral, happy, very_happy",
    "mood_score": "a float between 0 (very sad) and 10 (very happy)",
    "explanation": "brief explanation of the detected mood"
}}

Guidelines:
- very_sad (0-1.5): Expressing deep sadness, depression, hopelessness
- sad (1.5-3.5): Expressing sadness, disappointment, melancholy
- anxious (3.5-5): Expressing worry, stress, anxiety, overwhelm
- neutral (5-5.5): Neutral feelings, mixed emotions, no strong sentiment
- happy (5.5-8): Expressing happiness, contentment, satisfaction
- very_happy (8-10): Expressing joy, excitement, euphoria, celebration

Respond with ONLY the JSON object, nothing else."""

    def _validate_mood_category(self, mood: str) -> MoodCategory:
        """Validate and convert mood string to MoodCategory enum"""
        mood_lower = mood.lower().strip()
        
        # Map possible variations to enum values
        mood_mapping = {
            "very_sad": MoodCategory.VERY_SAD,
            "verysad": MoodCategory.VERY_SAD,
            "sad": MoodCategory.SAD,
            "anxious": MoodCategory.ANXIOUS,
            "anxiety": MoodCategory.ANXIOUS,
            "worried": MoodCategory.ANXIOUS,
            "neutral": MoodCategory.NEUTRAL,
            "okay": MoodCategory.NEUTRAL,
            "fine": MoodCategory.NEUTRAL,
            "happy": MoodCategory.HAPPY,
            "very_happy": MoodCategory.VERY_HAPPY,
            "veryhappy": MoodCategory.VERY_HAPPY,
            "joyful": MoodCategory.VERY_HAPPY,
            "excited": MoodCategory.VERY_HAPPY,
        }
        
        return mood_mapping.get(mood_lower, MoodCategory.NEUTRAL)


# Initialize global analyzer instance
sentiment_analyzer = SentimentAnalyzer()
