"""
Rufus AI Robot Companion - Main Bot Class
Integrates all components into a cohesive robot personality
"""

import logging
import threading
import time
from typing import Optional
from pathlib import Path

from config import (
    MEMORY_ENABLED, VISION_ENABLED,
    LOG_LEVEL, LOG_FILE
)
from src.arduino_controller import ArduinoController
from src.speech_to_text import SpeechToText
from src.text_to_speech import TextToSpeech
from src.conversation import ConversationManager
from src.emotion_detector import EmotionDetector
from src.gesture_controller import GestureController
from src.memory_system import MemorySystem
from src.vision_system import VisionSystem

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class RufusBot:
    """Main Rufus AI Robot Companion"""

    def __init__(self, enable_memory: bool = MEMORY_ENABLED, enable_vision: bool = VISION_ENABLED):
        """
        Initialize Rufus bot

        Args:
            enable_memory: Enable long-term memory system
            enable_vision: Enable camera/vision system
        """
        logger.info("=" * 50)
        logger.info("INITIALIZING RUFUS AI ROBOT COMPANION")
        logger.info("=" * 50)

        # Initialize Arduino connection
        logger.info("Connecting to Arduino...")
        self.arduino = ArduinoController()
        self.gestures = GestureController(self.arduino)

        # Initialize AI components
        logger.info("Initializing AI components...")
        self.stt = SpeechToText()
        self.tts = TextToSpeech()
        self.conversation = ConversationManager()
        self.emotion = EmotionDetector()

        # Initialize optional components
        self.memory = MemorySystem(enabled=enable_memory) if enable_memory else None
        self.vision = VisionSystem(enabled=enable_vision) if enable_vision else None

        # Start idle animations
        self.gestures.start_idle_animations()

        # Move servos to home position
        self.gestures.gesture_neutral()

        logger.info("Rufus initialized successfully!")
        logger.info("=" * 50)

    def listen(self) -> Optional[str]:
        """
        Listen to user voice input

        Returns:
            Transcribed text, or None if failed
        """
        logger.info("Listening...")
        return self.stt.listen()

    def think(self, user_input: str, use_memory: bool = True) -> str:
        """
        Generate response to user input

        Args:
            user_input: User's message
            use_memory: Whether to use long-term memory

        Returns:
            AI response
        """
        logger.info(f"User: {user_input}")

        # Detect emotion
        detected_emotion = self.emotion.detect_emotion(user_input)
        logger.debug(f"Detected emotion: {detected_emotion}")

        # Retrieve relevant memories if enabled
        context = ""
        if self.memory and use_memory:
            context = self.memory.get_context_for_response(user_input)
            if context:
                logger.debug(f"Retrieved {len(self.memory.retrieve_relevant_memories(user_input))} relevant memories")

        # Update system prompt with context
        if context:
            current_prompt = self.conversation.messages[0]["content"]
            enhanced_prompt = current_prompt + context
            # Note: This is a simplified approach - production would use proper context injection
            logger.debug("Added memory context to conversation")

        # Get AI response
        response = self.conversation.get_response(user_input)

        if not response:
            response = "I'm having trouble thinking right now. Could you try again?"

        logger.info(f"Rufus: {response}")

        # Store in memory if enabled
        if self.memory:
            self.memory.add_memory(
                user_input=user_input,
                bot_response=response,
                emotion=detected_emotion
            )

        return response

    def speak(self, text: str) -> bool:
        """
        Speak text aloud

        Args:
            text: Text to speak

        Returns:
            True if successful
        """
        return self.tts.speak(text)

    def respond(self, user_input: str) -> None:
        """
        Full response cycle: think + gesture + speak

        Args:
            user_input: User's message
        """
        # Think
        response = self.think(user_input)

        # Gesture based on response
        self.gestures.interpret_response_gesture(response)

        # Speak
        self.speak(response)

    def text_chat(self, user_input: str) -> None:
        """
        Text-based chat (no voice input)

        Args:
            user_input: User's message
        """
        self.respond(user_input)

    def voice_chat(self) -> None:
        """
        Voice-based chat (listen + respond)
        """
        user_input = self.listen()

        if not user_input:
            logger.warning("No input detected")
            return

        # Check for commands
        if user_input.lower().strip() in ["clear", "/clear", "reset"]:
            logger.info("Clearing conversation memory...")
            self.conversation.clear_memory()
            self.speak("I've forgotten our conversation. Ready to start fresh!")
            return

        self.respond(user_input)

    def look(self) -> Optional[str]:
        """
        Use vision system to describe what's seen

        Returns:
            Scene description
        """
        if not self.vision:
            return "Vision system is not enabled."

        return self.vision.describe_scene()

    def take_photo(self) -> Optional[str]:
        """
        Take a photo

        Returns:
            Path to photo file
        """
        if not self.vision:
            logger.error("Vision system is not enabled.")
            return None

        filepath = self.vision.take_photo()
        if filepath:
            logger.info(f"Photo saved: {filepath}")
            self.speak("I've taken a photo!")

        return filepath

    def get_memory_stats(self) -> dict:
        """
        Get memory system statistics

        Returns:
            Statistics dictionary
        """
        if not self.memory:
            return {"enabled": False}

        return self.memory.get_statistics()

    def clear_memory(self) -> None:
        """Clear all long-term memory"""
        if self.memory:
            self.memory.clear_all_memories()
            logger.info("Long-term memory cleared")

    def export_conversations(self) -> bool:
        """
        Export conversation history

        Returns:
            True if successful
        """
        if not self.memory:
            logger.warning("Memory system not enabled")
            return False

        return self.memory.export_conversations()

    def run_interactive(self) -> None:
        """Run interactive chat session"""
        logger.info("Starting interactive session...")
        logger.info("Commands: 'voice' for voice input, 'text <message>' for text, 'quit' to exit")

        self.speak("Hello! I'm Rufus, your AI robot companion. How can I help you today?")

        try:
            while True:
                try:
                    user_input = input("\n> ").strip()

                    if not user_input:
                        continue

                    if user_input.lower() in ["quit", "exit", "q"]:
                        logger.info("Shutting down...")
                        self.speak("Goodbye! It was great talking with you!")
                        break

                    elif user_input.lower() == "voice":
                        self.voice_chat()

                    elif user_input.lower().startswith("text "):
                        message = user_input[5:].strip()
                        self.text_chat(message)

                    elif user_input.lower() == "look":
                        description = self.look()
                        print(f"\nVision: {description}")
                        self.speak(description)

                    elif user_input.lower() == "photo":
                        self.take_photo()

                    elif user_input.lower() == "stats":
                        stats = self.get_memory_stats()
                        print(f"\nMemory Stats: {stats}")

                    elif user_input.lower() == "clear":
                        self.conversation.clear_memory()
                        self.clear_memory()
                        self.speak("Memory cleared. Ready for a fresh start!")

                    else:
                        # Default to text chat
                        self.text_chat(user_input)

                except KeyboardInterrupt:
                    logger.info("\nInterrupted by user")
                    break

        finally:
            self.shutdown()

    def shutdown(self) -> None:
        """Shutdown Rufus gracefully"""
        logger.info("Shutting down Rufus...")

        # Stop idle animations
        self.gestures.stop_idle_animations()

        # Move to home position
        self.gestures.gesture_neutral()

        # Release camera
        if self.vision:
            self.vision.shutdown()

        # Disconnect Arduino
        self.arduino.disconnect()

        logger.info("Rufus shutdown complete")
