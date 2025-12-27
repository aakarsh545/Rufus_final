"""
Speech to Text Module
Uses OpenAI Whisper API to convert voice to text
"""

import sounddevice as sd
import soundfile as sf
import openai
import logging
import os
from pathlib import Path
from typing import Optional
from config import (
    OPENAI_API_KEY, STT_MODEL,
    RECORDING_DURATION, SAMPLE_RATE, AUDIO_CHANNELS,
    DATA_DIR
)

logger = logging.getLogger(__name__)


class SpeechToText:
    """Convert voice input to text using Whisper API"""

    def __init__(self, api_key: str = OPENAI_API_KEY):
        """
        Initialize STT engine

        Args:
            api_key: OpenAI API key
        """
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set. Set it in environment or .env file.")

        openai.api_key = api_key
        self.temp_audio_file = DATA_DIR / "temp_recording.wav"

    def record_audio(self, duration: float = RECORDING_DURATION) -> Optional[str]:
        """
        Record audio from microphone

        Args:
            duration: Recording duration in seconds

        Returns:
            Path to recorded audio file, or None if failed
        """
        try:
            logger.info(f"Recording for {duration} seconds...")
            audio_data = sd.rec(
                int(duration * SAMPLE_RATE),
                samplerate=SAMPLE_RATE,
                channels=AUDIO_CHANNELS
            )
            sd.wait()  # Wait until recording is finished

            # Save to file
            sf.write(str(self.temp_audio_file), audio_data, SAMPLE_RATE)
            logger.info(f"Recording saved to {self.temp_audio_file}")
            return str(self.temp_audio_file)

        except Exception as e:
            logger.error(f"Failed to record audio: {e}")
            return None

    def transcribe(self, audio_path: Optional[str] = None) -> Optional[str]:
        """
        Transcribe audio file to text

        Args:
            audio_path: Path to audio file (uses last recording if not specified)

        Returns:
            Transcribed text, or None if failed
        """
        audio_file = audio_path or self.temp_audio_file

        if not os.path.exists(audio_file):
            logger.error(f"Audio file not found: {audio_file}")
            return None

        try:
            with open(audio_file, "rb") as audio:
                response = openai.audio.transcriptions.create(
                    model=STT_MODEL,
                    file=audio
                )
            text = response.text.strip()
            logger.info(f"Transcribed: {text}")
            return text

        except Exception as e:
            logger.error(f"Failed to transcribe audio: {e}")
            return None

    def listen(self, duration: float = RECORDING_DURATION) -> Optional[str]:
        """
        Convenience method: Record and transcribe in one call

        Args:
            duration: Recording duration

        Returns:
            Transcribed text
        """
        audio_path = self.record_audio(duration)
        if audio_path:
            return self.transcribe(audio_path)
        return None

    def cleanup(self):
        """Remove temporary audio files"""
        if self.temp_audio_file.exists():
            self.temp_audio_file.unlink()
