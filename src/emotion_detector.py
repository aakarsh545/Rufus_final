"""
Emotion Detection Module
Detects emotions from user input and triggers appropriate gestures
"""

import logging
import random
from typing import Optional, List
from config import EMOTION_KEYWORDS

logger = logging.getLogger(__name__)


class EmotionDetector:
    """Detects emotions in user messages and suggests gestures"""

    # Emotion to gesture mappings
    EMOTION_GESTURES = {
        "happy": ["yes", "natural_movement"],
        "sad": ["neutral"],
        "curious": ["head_tilt"],
        "surprised": ["head_tilt", "natural_movement"],
        "thinking": ["neutral", "natural_movement"]
    }

    def __init__(self):
        """Initialize emotion detector"""
        self.current_emotion = "neutral"

    def detect_emotion(self, text: str) -> str:
        """
        Detect emotion from text based on keywords

        Args:
            text: User message to analyze

        Returns:
            Detected emotion string
        """
        text_lower = text.lower()

        # Check each emotion category
        for emotion, keywords in EMOTION_KEYWORDS.items():
            if any(keyword in text_lower for keyword in keywords):
                self.current_emotion = emotion
                logger.debug(f"Detected emotion: {emotion}")
                return emotion

        self.current_emotion = "neutral"
        return "neutral"

    def suggest_gestures(self, emotion: Optional[str] = None) -> List[str]:
        """
        Suggest appropriate gestures for detected emotion

        Args:
            emotion: Emotion to get gestures for (uses current if not specified)

        Returns:
            List of gesture names
        """
        emotion = emotion or self.current_emotion

        if emotion in self.EMOTION_GESTURES:
            gestures = self.EMOTION_GESTURES[emotion]
            return gestures

        return ["neutral"]

    def get_response_style(self, emotion: Optional[str] = None) -> str:
        """
        Get suggested response style based on emotion

        Args:
            emotion: Emotion to analyze (uses current if not specified)

        Returns:
            Response style descriptor
        """
        emotion = emotion or self.current_emotion

        styles = {
            "happy": "enthusiastic and warm",
            "sad": "comforting and gentle",
            "curious": "engaged and inquisitive",
            "surprised": "excited and amazed",
            "thinking": "thoughtful and contemplative",
            "neutral": "friendly and conversational"
        }

        return styles.get(emotion, "friendly and conversational")

    def analyze_sentiment(self, text: str) -> dict:
        """
        Analyze sentiment of text (basic keyword-based)

        Args:
            text: Text to analyze

        Returns:
            Dictionary with sentiment scores
        """
        text_lower = text.lower()

        # Simple sentiment scoring
        positive_words = ["good", "great", "awesome", "happy", "love", "wonderful", "fantastic", "excellent"]
        negative_words = ["bad", "sad", "terrible", "hate", "awful", "horrible", "upset", "angry"]

        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        total = positive_count + negative_count
        if total == 0:
            return {"sentiment": "neutral", "confidence": 0.5}

        positive_ratio = positive_count / total

        if positive_ratio > 0.6:
            sentiment = "positive"
        elif positive_ratio < 0.4:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        confidence = abs(positive_ratio - 0.5) * 2  # 0 to 1

        return {
            "sentiment": sentiment,
            "confidence": confidence
        }
