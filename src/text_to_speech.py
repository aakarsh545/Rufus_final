"""
Text to Speech Module
Uses OpenAI TTS API to convert text to speech
"""

import openai
import logging
import os
from pathlib import Path
from config import (
    OPENAI_API_KEY, TTS_MODEL, TTS_VOICE,
    DATA_DIR
)

logger = logging.getLogger(__name__)


class TextToSpeech:
    """Convert text to speech using OpenAI TTS API"""

    def __init__(self, api_key: str = OPENAI_API_KEY, voice: str = TTS_VOICE):
        """
        Initialize TTS engine

        Args:
            api_key: OpenAI API key
            voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
        """
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set. Set it in environment or .env file.")

        openai.api_key = api_key
        self.voice = voice
        self.output_file = DATA_DIR / "rufus_tts.mp3"

    def generate_speech(self, text: str, output_path: Optional[str] = None) -> bool:
        """
        Generate speech from text

        Args:
            text: Text to convert to speech
            output_path: Output MP3 file path (uses default if not specified)

        Returns:
            True if successful
        """
        if not text.strip():
            logger.warning("Empty text provided for TTS")
            return False

        output = output_path or str(self.output_file)

        try:
            response = openai.audio.speech.create(
                model=TTS_MODEL,
                voice=self.voice,
                input=text
            )

            response.stream_to_file(output)
            logger.info(f"Speech generated: {output}")
            return True

        except Exception as e:
            logger.error(f"Failed to generate speech: {e}")
            return False

    def speak(self, text: str) -> bool:
        """
        Generate speech and play it through system speakers

        Args:
            text: Text to speak

        Returns:
            True if successful
        """
        if not self.generate_speech(text):
            return False

        # Play using system audio player
        try:
            import platform
            system = platform.system()

            if system == "Darwin":  # macOS
                os.system(f"afplay {self.output_file}")
            elif system == "Linux":
                os.system(f"aplay {self.output_file}")
            elif system == "Windows":
                os.system(f"start {self.output_file}")
            else:
                logger.warning(f"Unsupported platform: {system}")
                return False

            return True

        except Exception as e:
            logger.error(f"Failed to play audio: {e}")
            return False

    def set_voice(self, voice: str) -> None:
        """
        Change TTS voice

        Args:
            voice: New voice (alloy, echo, fable, onyx, nova, shimmer)
        """
        valid_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        if voice in valid_voices:
            self.voice = voice
            logger.info(f"Voice changed to: {voice}")
        else:
            logger.warning(f"Invalid voice: {voice}. Valid options: {valid_voices}")
