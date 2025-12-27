"""
Vision/Camera System
Provides object detection, face recognition, and image understanding
"""

import cv2
import logging
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import numpy as np
from config import (
    VISION_ENABLED, CAMERA_INDEX,
    OBJECT_DETECTION_CONFIDENCE, FACE_RECOGNITION_ENABLED,
    DATA_DIR
)

logger = logging.getLogger(__name__)


class VisionSystem:
    """Computer vision system for Rufus"""

    def __init__(self, enabled: bool = VISION_ENABLED):
        """
        Initialize vision system

        Args:
            enabled: Whether vision system is enabled
        """
        self.enabled = enabled
        self.camera: Optional[cv2.VideoCapture] = None

        if not self.enabled:
            logger.info("Vision system disabled")
            return

        try:
            # Initialize camera
            self.camera = cv2.VideoCapture(CAMERA_INDEX)

            if not self.camera.isOpened():
                logger.error(f"Failed to open camera {CAMERA_INDEX}")
                self.enabled = False
                return

            # Set camera properties
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

            logger.info(f"Vision system initialized (camera {CAMERA_INDEX})")

        except Exception as e:
            logger.error(f"Failed to initialize vision system: {e}")
            self.enabled = False

    def capture_frame(self) -> Optional[np.ndarray]:
        """
        Capture a single frame from camera

        Returns:
            Image array, or None if failed
        """
        if not self.enabled or not self.camera:
            return None

        try:
            ret, frame = self.camera.read()

            if not ret:
                logger.error("Failed to capture frame")
                return None

            return frame

        except Exception as e:
            logger.error(f"Failed to capture frame: {e}")
            return None

    def save_frame(self, frame: np.ndarray, filename: str = "capture.jpg") -> bool:
        """
        Save frame to file

        Args:
            frame: Image array
            filename: Output filename

        Returns:
            True if successful
        """
        try:
            filepath = DATA_DIR / filename
            cv2.imwrite(str(filepath), frame)
            logger.debug(f"Frame saved to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Failed to save frame: {e}")
            return False

    def detect_faces(self, frame: Optional[np.ndarray] = None) -> List[Dict]:
        """
        Detect faces in image

        Args:
            frame: Image array (captures new frame if not provided)

        Returns:
            List of face detections with bounding boxes
        """
        if not self.enabled:
            return []

        try:
            if frame is None:
                frame = self.capture_frame()
                if frame is None:
                    return []

            # Use OpenCV's Haar cascade for face detection
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )

            detections = []
            for (x, y, w, h) in faces:
                detections.append({
                    "bbox": (int(x), int(y), int(w), int(h)),
                    "center": (int(x + w/2), int(y + h/2)),
                    "size": int(w * h)
                })

            logger.debug(f"Detected {len(detections)} face(s)")
            return detections

        except Exception as e:
            logger.error(f"Failed to detect faces: {e}")
            return []

    def detect_objects(self, frame: Optional[np.ndarray] = None) -> List[Dict]:
        """
        Detect objects using simple methods (motion/color detection)

        Args:
            frame: Image array

        Returns:
            List of detected objects
        """
        if not self.enabled:
            return []

        try:
            if frame is None:
                frame = self.capture_frame()
                if frame is None:
                    return []

            # Simple color-based detection (can be extended)
            # This is a placeholder - real implementation would use YOLO or similar
            objects = []

            # Detect bright objects (potential highlights)
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            bright_mask = cv2.inRange(hsv, (0, 0, 200), (180, 30, 255))
            contours, _ = cv2.findContours(bright_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 100:
                    x, y, w, h = cv2.boundingRect(contour)
                    objects.append({
                        "type": "bright_object",
                        "bbox": (int(x), int(y), int(w), int(h)),
                        "area": int(area)
                    })

            logger.debug(f"Detected {len(objects)} object(s)")
            return objects

        except Exception as e:
            logger.error(f"Failed to detect objects: {e}")
            return []

    def describe_scene(self, frame: Optional[np.ndarray] = None) -> str:
        """
        Generate a textual description of the scene

        Args:
            frame: Image array

        Returns:
            Scene description
        """
        if not self.enabled:
            return "Vision system is disabled."

        try:
            if frame is None:
                frame = self.capture_frame()
                if frame is None:
                    return "Unable to capture frame."

            # Get basic scene info
            height, width = frame.shape[:2]
            faces = self.detect_faces(frame)

            description = f"I can see a {width}x{height} image."

            if faces:
                description += f" There {'is' if len(faces) == 1 else 'are'} {len(faces)} face{'s' if len(faces) > 1 else ''} visible."

            # Get dominant colors
            avg_color = frame.mean(axis=0).mean(axis=0)
            brightness = avg_color.mean()

            if brightness < 50:
                description += " The scene appears dark."
            elif brightness > 200:
                description += " The scene appears very bright."
            else:
                description += " The lighting looks normal."

            return description

        except Exception as e:
            logger.error(f"Failed to describe scene: {e}")
            return "Unable to describe the scene."

    def take_photo(self, filename: Optional[str] = None) -> Optional[str]:
        """
        Take and save a photo

        Args:
            filename: Output filename (auto-generated if not provided)

        Returns:
            Path to saved photo, or None if failed
        """
        if not self.enabled:
            return None

        try:
            frame = self.capture_frame()
            if frame is None:
                return None

            if filename is None:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"rufus_photo_{timestamp}.jpg"

            if self.save_frame(frame, filename):
                return str(DATA_DIR / filename)

            return None

        except Exception as e:
            logger.error(f"Failed to take photo: {e}")
            return None

    def motion_detected(self, prev_frame: np.ndarray, current_frame: np.ndarray, threshold: int = 25) -> bool:
        """
        Detect motion between two frames

        Args:
            prev_frame: Previous frame
            current_frame: Current frame
            threshold: Motion detection threshold

        Returns:
            True if motion detected
        """
        if not self.enabled:
            return False

        try:
            # Convert to grayscale
            prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
            curr_gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)

            # Calculate absolute difference
            diff = cv2.absdiff(prev_gray, curr_gray)

            # Apply threshold
            _, thresh = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)

            # Count white pixels
            motion_pixels = cv2.countNonZero(thresh)
            total_pixels = thresh.shape[0] * thresh.shape[1]

            motion_ratio = motion_pixels / total_pixels

            # Motion if > 1% of pixels changed
            return motion_ratio > 0.01

        except Exception as e:
            logger.error(f"Failed to detect motion: {e}")
            return False

    def get_camera_info(self) -> Dict:
        """
        Get camera information

        Returns:
            Camera info dictionary
        """
        if not self.enabled or not self.camera:
            return {"enabled": False}

        try:
            width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(self.camera.get(cv2.CAP_PROP_FPS))

            return {
                "enabled": True,
                "camera_index": CAMERA_INDEX,
                "resolution": f"{width}x{height}",
                "fps": fps
            }

        except Exception as e:
            logger.error(f"Failed to get camera info: {e}")
            return {"enabled": True, "error": str(e)}

    def shutdown(self) -> None:
        """Release camera resources"""
        if self.camera:
            self.camera.release()
            logger.info("Camera released")
