"""
Gesture Controller
Manages robot gestures and animations
"""

import logging
import time
import random
import threading
from typing import Optional
from config import (
    IDLE_ANIMATION_INTERVAL_MIN,
    IDLE_ANIMATION_INTERVAL_MAX
)

logger = logging.getLogger(__name__)


class GestureController:
    """Controls robot gestures and animations"""

    def __init__(self, arduino_controller):
        """
        Initialize gesture controller

        Args:
            arduino_controller: ArduinoController instance
        """
        self.arduino = arduino_controller
        self.idle_animation_thread: Optional[threading.Thread] = None
        self.idle_animation_running = False

    def gesture_yes(self) -> None:
        """Perform 'yes' gesture (nodding)"""
        logger.info("Gesture: YES")
        self.arduino.gesture_yes()

    def gesture_no(self) -> None:
        """Perform 'no' gesture (shaking)"""
        logger.info("Gesture: NO")
        self.arduino.gesture_no()

    def gesture_neutral(self) -> None:
        """Return to neutral position"""
        logger.info("Gesture: NEUTRAL")
        self.arduino.gesture_neutral()

    def gesture_head_tilt(self) -> None:
        """Tilt head to show curiosity"""
        logger.info("Gesture: HEAD TILT")
        # Tilt head slightly
        self.arduino.move_servo("head", 100)
        time.sleep(1)
        self.arduino.move_servo("head", 80)  # Return to home

    def gesture_thinking(self) -> None:
        """Perform thinking gesture"""
        logger.info("Gesture: THINKING")
        # Head tilt + slight movement
        self.arduino.move_servo("head", 70)
        time.sleep(0.5)
        self.arduino.move_servo("head", 90)
        time.sleep(0.5)
        self.arduino.move_servo("head", 80)

    def gesture_wave(self) -> None:
        """Wave with arm"""
        logger.info("Gesture: WAVE")
        # Wave with right arm
        angles = [135, 150, 135, 150, 135]
        for angle in angles:
            self.arduino.move_servo("right_arm", angle)
            time.sleep(0.2)

    def gesture_excited(self) -> None:
        """Excited movement (both arms)"""
        logger.info("Gesture: EXCITED")
        # Quick movements with both arms
        for _ in range(3):
            self.arduino.move_servo("left_arm", 60)
            self.arduino.move_servo("right_arm", 150)
            time.sleep(0.2)
            self.arduino.move_servo("left_arm", 40)
            self.arduino.move_servo("right_arm", 135)
            time.sleep(0.2)

    def natural_movement(self) -> None:
        """Random subtle movement"""
        logger.debug("Natural movement")
        self.arduino.natural_movement()

    def perform_gesture(self, gesture_name: str) -> bool:
        """
        Perform a named gesture

        Args:
            gesture_name: Name of gesture to perform

        Returns:
            True if gesture found and performed
        """
        gestures = {
            "yes": self.gesture_yes,
            "no": self.gesture_no,
            "neutral": self.gesture_neutral,
            "head_tilt": self.gesture_head_tilt,
            "thinking": self.gesture_thinking,
            "wave": self.gesture_wave,
            "excited": self.gesture_excited,
            "natural_movement": self.natural_movement
        }

        if gesture_name in gestures:
            gestures[gesture_name]()
            return True

        logger.warning(f"Unknown gesture: {gesture_name}")
        return False

    def start_idle_animations(self) -> None:
        """Start background thread for idle animations"""
        if self.idle_animation_running:
            logger.warning("Idle animations already running")
            return

        self.idle_animation_running = True
        self.idle_animation_thread = threading.Thread(target=self._idle_animation_loop, daemon=True)
        self.idle_animation_thread.start()
        logger.info("Idle animations started")

    def stop_idle_animations(self) -> None:
        """Stop idle animation thread"""
        self.idle_animation_running = False
        if self.idle_animation_thread:
            self.idle_animation_thread.join(timeout=2)
        logger.info("Idle animations stopped")

    def _idle_animation_loop(self) -> None:
        """Background loop for random idle animations"""
        while self.idle_animation_running:
            # Random interval between animations
            interval = random.uniform(
                IDLE_ANIMATION_INTERVAL_MIN,
                IDLE_ANIMATION_INTERVAL_MAX
            )
            time.sleep(interval)

            if not self.idle_animation_running:
                break

            # Perform random subtle movement
            self.natural_movement()

    def interpret_response_gesture(self, ai_response: str) -> None:
        """
        Analyze AI response and perform appropriate gesture

        Args:
            ai_response: Text response from AI
        """
        response_lower = ai_response.lower()

        # Yes indicators
        if any(word in response_lower for word in ["yes", "yeah", "yep", "absolutely", "definitely", "certainly"]):
            self.gesture_yes()

        # No indicators
        elif any(word in response_lower for word in ["no", "nope", "not really", "unfortunately"]):
            self.gesture_no()

        # Questioning/curious
        elif any(word in response_lower for word in ["hmm", "interesting", "let me think", "i wonder"]):
            self.gesture_thinking()

        # Excited
        elif any(word in response_lower for word in ["wow", "amazing", "excited", "great", "awesome"]):
            self.gesture_excited()

        # Default: subtle movement
        else:
            # 30% chance of natural movement for variety
            if random.random() < 0.3:
                self.natural_movement()
