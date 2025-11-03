"""
Gun gesture detection using MediaPipe Hands.
"""

import mediapipe as mp
import cv2
import numpy as np
from typing import Optional, Tuple


class HeartDetector:
    """Detects gun gestures using hand landmarks."""

    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,  # Only need one hand for gun gesture
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.last_shoot_position = None
        self.shoot_detected = False
        self.aiming = False  # True when gun is horizontal (aiming)
        self.aiming_position = None

    def _is_finger_extended(self, landmarks, finger_tip_idx: int, finger_pip_idx: int) -> bool:
        """
        Check if a finger is extended.

        Args:
            landmarks: Hand landmarks
            finger_tip_idx: Index of finger tip landmark
            finger_pip_idx: Index of finger PIP (middle joint) landmark

        Returns:
            True if finger is extended (tip is higher than PIP joint in image space)
        """
        tip_y = landmarks.landmark[finger_tip_idx].y
        pip_y = landmarks.landmark[finger_pip_idx].y

        # In image coordinates, smaller y = higher position
        # Finger is extended if tip is significantly higher than PIP
        # Relaxed threshold from 0.03 to 0.015 for better detection
        return tip_y < pip_y - 0.015

    def _detect_gun_gesture(self, landmarks) -> Tuple[Optional[Tuple[int, int]], bool, Optional[Tuple[int, int]]]:
        """
        Detect gun gesture from a single hand.

        Gun gesture:
        - Index finger extended (pointing)
        - Other fingers curled
        - Thumb extended (perpendicular to index)

        Returns:
            Tuple of (shoot_position, is_aiming, aiming_position)
            - shoot_position: Position if gun is vertical (shoot), None otherwise
            - is_aiming: True if gun is horizontal (aiming)
            - aiming_position: Position for aiming reticle
        """
        # Landmark indices
        INDEX_TIP = 8
        INDEX_PIP = 6
        MIDDLE_TIP = 12
        MIDDLE_PIP = 10
        RING_TIP = 16
        RING_PIP = 14
        PINKY_TIP = 20
        PINKY_PIP = 18
        THUMB_TIP = 4
        WRIST = 0

        # Get key points
        index_tip = landmarks.landmark[INDEX_TIP]
        wrist = landmarks.landmark[WRIST]

        # Position for aiming/shooting (index finger tip)
        position = (int(index_tip.x * 1000), int(index_tip.y * 1000))

        # Check if index finger is extended
        index_extended = self._is_finger_extended(landmarks, INDEX_TIP, INDEX_PIP)

        # Check if other fingers are NOT extended (curled)
        middle_curled = not self._is_finger_extended(landmarks, MIDDLE_TIP, MIDDLE_PIP)
        ring_curled = not self._is_finger_extended(landmarks, RING_TIP, RING_PIP)
        pinky_curled = not self._is_finger_extended(landmarks, PINKY_TIP, PINKY_PIP)

        # Strict gun gesture: index extended + all others curled
        is_strict_gun = index_extended and middle_curled and ring_curled and pinky_curled

        # Calculate gun direction vector (from wrist to index tip)
        dx = index_tip.x - wrist.x
        dy = index_tip.y - wrist.y

        # Calculate angle (in radians)
        angle = np.arctan2(dy, dx)
        angle_degrees = np.degrees(angle)

        # Normalize angle to 0-360
        if angle_degrees < 0:
            angle_degrees += 360

        # Check orientation:
        # Shoot condition: Gun pointing UP (225-315 degrees) + strict gun gesture
        if 225 <= angle_degrees <= 315 and is_strict_gun:
            return position, False, None

        # Aiming condition: Hand is detected (loose - always show reticle)
        else:
            return None, True, position

    def detect(self, frame) -> Tuple[bool, Optional[Tuple[int, int]], bool, Optional[Tuple[int, int]], Optional[np.ndarray]]:
        """
        Detect gun gesture in the frame.

        Returns:
            Tuple of (shoot_detected, shoot_position, is_aiming, aiming_position, debug_frame)
            - shoot_detected: Boolean indicating if gun is pointing up (shoot)
            - shoot_position: (x, y) normalized coordinates (0-1000) or None
            - is_aiming: Boolean indicating if gun is horizontal (aiming)
            - aiming_position: (x, y) position for aiming reticle or None
            - debug_frame: Frame with hand landmarks drawn or None
        """
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame
        results = self.hands.process(rgb_frame)

        # Create debug frame with landmarks
        debug_frame = self.get_debug_frame(frame, results)

        if not results.multi_hand_landmarks:
            self.shoot_detected = False
            self.last_shoot_position = None
            self.aiming = False
            self.aiming_position = None
            return False, None, False, None, debug_frame

        # Detect gun gesture from first hand
        for hand_landmarks in results.multi_hand_landmarks:
            shoot_pos, is_aiming, aim_pos = self._detect_gun_gesture(hand_landmarks)

            if shoot_pos:
                # Gun pointing up - shoot!
                self.shoot_detected = True
                self.last_shoot_position = shoot_pos
                self.aiming = False
                self.aiming_position = None
                return True, shoot_pos, False, None, debug_frame

            elif is_aiming:
                # Gun horizontal - aiming
                self.shoot_detected = False
                self.last_shoot_position = None
                self.aiming = True
                self.aiming_position = aim_pos
                return False, None, True, aim_pos, debug_frame

        # No gun gesture detected
        self.shoot_detected = False
        self.last_shoot_position = None
        self.aiming = False
        self.aiming_position = None
        return False, None, False, None, debug_frame

    def get_debug_frame(self, frame, results=None) -> np.ndarray:
        """
        Get debug frame with hand landmarks drawn.
        Useful for testing and calibration.
        """
        if results is None:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)

        debug_frame = frame.copy()

        if results.multi_hand_landmarks:
            mp_drawing = mp.solutions.drawing_utils
            mp_drawing_styles = mp.solutions.drawing_styles

            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    debug_frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style()
                )

        # Draw detection state
        status_text = "NO HAND"
        status_color = (128, 128, 128)  # Gray

        if self.shoot_detected:
            status_text = "SHOOTING!"
            status_color = (0, 0, 255)  # Red
        elif self.aiming:
            status_text = "AIMING"
            status_color = (0, 255, 255)  # Yellow
        elif results.multi_hand_landmarks:
            status_text = "HAND DETECTED"
            status_color = (0, 255, 0)  # Green

        # Draw status text on frame
        cv2.putText(debug_frame, status_text, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, status_color, 2)

        return debug_frame

    def release(self):
        """Release MediaPipe resources."""
        if self.hands:
            self.hands.close()
            self.hands = None

    def __del__(self):
        """Cleanup on deletion."""
        self.release()
