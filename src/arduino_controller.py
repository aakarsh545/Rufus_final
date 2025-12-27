"""
Arduino Serial Communication Controller
Handles communication between Python and Arduino Uno via serial port
"""

import serial
import serial.tools.list_ports
import time
import logging
from typing import Optional, Dict, Tuple
from config import (
    SERIAL_PORT, BAUD_RATE, SERIAL_TIMEOUT,
    SERVO_HOME_POSITIONS, SERVO_PINS
)

logger = logging.getLogger(__name__)


class ArduinoController:
    """Manages serial communication with Arduino Uno"""

    def __init__(self, port: str = SERIAL_PORT, baudrate: int = BAUD_RATE):
        """
        Initialize Arduino controller

        Args:
            port: Serial port path (auto-detects if not found)
            baudrate: Serial communication speed
        """
        self.port = self._detect_port(port)
        self.baudrate = baudrate
        self.connection: Optional[serial.Serial] = None
        self._connect()

    def _detect_port(self, preferred_port: str) -> str:
        """
        Auto-detect Arduino port if preferred port not found

        Args:
            preferred_port: User-specified port

        Returns:
            Detected port path
        """
        ports = serial.tools.list_ports.comports()
        arduino_ports = [
            p.device for p in ports
            if 'Arduino' in p.description or
               'CH340' in p.description or  # Common USB-Serial
               'usbserial' in p.device.lower() or
               'cu.usb' in p.device  # Mac USB-Serial
        ]

        if arduino_ports:
            detected = arduino_ports[0]
            if detected != preferred_port:
                logger.info(f"Auto-detected Arduino port: {detected}")
            return detected

        return preferred_port

    def _connect(self) -> None:
        """Establish serial connection with Arduino"""
        try:
            self.connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=SERIAL_TIMEOUT
            )
            time.sleep(2)  # Wait for Arduino to reset
            logger.info(f"Connected to Arduino on {self.port}")
        except serial.SerialException as e:
            logger.error(f"Failed to connect to Arduino: {e}")
            logger.warning("Running in SIMULATION mode (no hardware)")
            self.connection = None

    def send_command(self, command: str) -> bool:
        """
        Send command to Arduino

        Args:
            command: Command string (e.g., "yes", "no", "head_90")

        Returns:
            True if successful, False otherwise
        """
        if not self.connection:
            logger.debug(f"[SIMULATION] Command: {command}")
            return True

        try:
            self.connection.write(f"{command}\n".encode())
            self.connection.flush()
            logger.debug(f"Sent: {command}")
            return True
        except serial.SerialException as e:
            logger.error(f"Failed to send command '{command}': {e}")
            return False

    def gesture_yes(self) -> None:
        """Trigger 'yes' gesture (right arm nods 3x)"""
        self.send_command("yes")

    def gesture_no(self) -> None:
        """Trigger 'no' gesture (head shakes 2x)"""
        self.send_command("no")

    def gesture_neutral(self) -> None:
        """Return to neutral/home position"""
        self.send_command("neutral")

    def move_servo(self, servo: str, angle: int) -> bool:
        """
        Move specific servo to angle

        Args:
            servo: Servo name ('head', 'left_arm', 'right_arm')
            angle: Target angle (0-180)

        Returns:
            True if successful
        """
        if servo not in SERVO_PINS:
            logger.error(f"Unknown servo: {servo}")
            return False

        command = f"{servo}_{angle}"
        return self.send_command(command)

    def play_audio(self, filename: str = "rufus_tts.mp3") -> bool:
        """
        Trigger audio playback on VS1053

        Args:
            filename: Audio file to play

        Returns:
            True if successful
        """
        return self.send_command(f"PLAY {filename}")

    def set_home_position(self) -> None:
        """Move all servos to home position"""
        for servo, angle in SERVO_HOME_POSITIONS.items():
            self.move_servo(servo, angle)

    def natural_movement(self) -> None:
        """Trigger a random natural movement"""
        import random
        servo = random.choice(list(SERVO_PINS.keys()))
        current_angle = SERVO_HOME_POSITIONS[servo]

        # Small random movement (+/- 15 degrees)
        new_angle = current_angle + random.randint(-15, 15)
        new_angle = max(0, min(180, new_angle))

        self.move_servo(servo, new_angle)

        # Return to home after short delay
        time.sleep(0.5)
        self.move_servo(servo, current_angle)

    def disconnect(self) -> None:
        """Close serial connection"""
        if self.connection and self.connection.is_open:
            self.connection.close()
            logger.info("Disconnected from Arduino")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
