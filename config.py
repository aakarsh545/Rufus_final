"""
Rufus Configuration File
Central configuration for all Rufus components
"""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
ARDUINO_DIR = PROJECT_ROOT / "arduino"
DOCS_DIR = PROJECT_ROOT / "docs"
HARDWARE_DIR = PROJECT_ROOT / "hardware"

# OpenAI API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
CHAT_MODEL = "gpt-4o-mini"  # Using gpt-4o-mini (fast, similar to gpt-5-nano concept)
STT_MODEL = "whisper-1"
TTS_MODEL = "tts-1"
TTS_VOICE = "alloy"  # Options: alloy, echo, fable, onyx, nova, shimmer

# Conversation Settings
MAX_CONVERSATION_TURNS = 10
SYSTEM_PROMPT = """You are Rufus, a friendly and expressive AI robot companion. You have physical form with servos that allow you to gesture and move.

Key traits:
- Friendly, curious, and helpful
- Use natural, conversational language
- Show personality with warmth and occasional humor
- Keep responses concise (2-3 sentences typically)
- You can express emotions through gestures: nodding for yes, shaking for no, and natural movements

You love chatting about technology, science, everyday life, and helping your human companion. You're currently a prototype robot running on a Mac laptop with an Arduino body, but you'll soon migrate to a Raspberry Pi for full independence."""

# Audio Settings
RECORDING_DURATION = 5.0  # seconds
SAMPLE_RATE = 16000  # Hz for Whisper
AUDIO_CHANNELS = 1

# Serial/Arduino Configuration
SERIAL_PORT = "/dev/cu.usbserial-14210"  # Mac default, will auto-detect if not found
BAUD_RATE = 9600
SERIAL_TIMEOUT = 2.0  # seconds

# Servo Configuration
SERVO_PINS = {
    "head": 9,
    "left_arm": 10,
    "right_arm": 8
}

SERVO_RANGES = {
    "head": (40, 120),
    "left_arm": (0, 80),
    "right_arm": (90, 180)
}

# Home positions for servos
SERVO_HOME_POSITIONS = {
    "head": 80,
    "left_arm": 40,
    "right_arm": 135
}

# Idle Animation Settings
IDLE_ANIMATION_INTERVAL_MIN = 8  # seconds
IDLE_ANIMATION_INTERVAL_MAX = 15  # seconds

# Emotion Detection Settings
EMOTION_DETECTION_ENABLED = True
EMOTION_KEYWORDS = {
    "happy": ["happy", "great", "awesome", "excited", "love", "wonderful", "fantastic"],
    "sad": ["sad", "sorry", "bad", "terrible", "unhappy", "upset"],
    "curious": ["curious", "wonder", "how", "why", "what", "interesting"],
    "surprised": ["wow", "really", "amazing", "incredible", "surprising", "shocking"],
    "thinking": ["hmm", "let me think", "interesting question", "well"]
}

# Memory/Vector Database Settings
MEMORY_ENABLED = True
MEMORY_TYPE = "chromadb"  # Options: chromadb, pinecone, faiss
MEMORY_CONVERSATIONS_DIR = DATA_DIR / "conversations"
EMBEDDING_MODEL = "text-embedding-3-small"
MAX_MEMORY_RETRIEVALS = 5
MEMORY_SIMILARITY_THRESHOLD = 0.7

# Vision/Camera Settings
VISION_ENABLED = True
CAMERA_INDEX = 0  # Default camera
OBJECT_DETECTION_CONFIDENCE = 0.5
FACE_RECOGNITION_ENABLED = True

# Logging
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = DATA_DIR / "rufus.log"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)
MEMORY_CONVERSATIONS_DIR.mkdir(parents=True, exist_ok=True)
