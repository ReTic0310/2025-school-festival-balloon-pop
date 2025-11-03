"""
Camera management module with device registration and auto-detection.
"""

import cv2
import json
import subprocess
import re
from pathlib import Path
from typing import Optional, Dict, Tuple


class CameraManager:
    """Manages USB camera detection and configuration."""

    def __init__(self, config_path: str = "camera_config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.camera = None
        self.device_path = None

    def _load_config(self) -> Dict:
        """Load camera configuration from JSON file."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return {"registered_cameras": []}

    def _get_device_info(self, device_path: str) -> Optional[Dict]:
        """Get detailed device information using v4l2-ctl."""
        try:
            result = subprocess.run(
                ['v4l2-ctl', '-d', device_path, '--info', '--list-formats-ext'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                return None

            output = result.stdout
            info = {}

            # Extract card (model name)
            card_match = re.search(r'Card type\s*:\s*(.+)', output)
            if card_match:
                info['model'] = card_match.group(1).strip()

            # Extract serial number
            serial_match = re.search(r'Serial\s*:\s*(\w+)', output)
            if serial_match:
                info['serial'] = serial_match.group(1).strip()

            # Extract bus info
            bus_match = re.search(r'Bus info\s*:\s*(.+)', output)
            if bus_match:
                info['bus_info'] = bus_match.group(1).strip()

            # Extract driver
            driver_match = re.search(r'Driver name\s*:\s*(.+)', output)
            if driver_match:
                info['driver'] = driver_match.group(1).strip()

            return info if info else None

        except (subprocess.TimeoutExpired, FileNotFoundError):
            return None

    def find_registered_camera(self) -> Optional[str]:
        """Find a registered camera by matching serial number."""
        if not self.config.get("registered_cameras"):
            return None

        # Check common video device paths
        for i in range(10):
            device_path = f"/dev/video{i}"
            if not Path(device_path).exists():
                continue

            device_info = self._get_device_info(device_path)
            if not device_info or 'serial' not in device_info:
                continue

            # Match against registered cameras
            for registered in self.config["registered_cameras"]:
                if device_info['serial'] == registered.get('serial'):
                    print(f"Found registered camera: {registered['model']} at {device_path}")

                    # Update last_seen_device in config
                    registered['last_seen_device'] = device_path
                    self._save_config()

                    return device_path

        return None

    def _save_config(self):
        """Save camera configuration to JSON file."""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

    def initialize(self) -> bool:
        """Initialize camera using registered device or fallback."""
        # Try to find registered camera
        device_path = self.find_registered_camera()

        # Fallback to last seen device
        if not device_path and self.config.get("registered_cameras"):
            last_seen = self.config["registered_cameras"][0].get("last_seen_device")
            if last_seen and Path(last_seen).exists():
                device_path = last_seen
                print(f"Using last seen device: {device_path}")

        # Fallback to /dev/video0
        if not device_path:
            device_path = "/dev/video0"
            print(f"Using default device: {device_path}")

        # Open camera
        self.device_path = device_path
        self.camera = cv2.VideoCapture(device_path)

        if not self.camera.isOpened():
            print(f"Failed to open camera at {device_path}")
            return False

        # Set preferred settings from config
        if self.config.get("registered_cameras"):
            cam_config = self.config["registered_cameras"][0]

            # Set resolution
            if "preferred_resolution" in cam_config:
                width, height = cam_config["preferred_resolution"]
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

            # Set FPS
            if "preferred_fps" in cam_config:
                self.camera.set(cv2.CAP_PROP_FPS, cam_config["preferred_fps"])

            # Set MJPEG format if preferred
            if cam_config.get("preferred_format") == "MJPG":
                self.camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

        # Verify actual settings
        actual_width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
        actual_fps = int(self.camera.get(cv2.CAP_PROP_FPS))

        print(f"Camera initialized: {actual_width}x{actual_height} @ {actual_fps}fps")
        return True

    def read_frame(self) -> Optional[Tuple]:
        """Read a frame from the camera."""
        if self.camera is None:
            return None

        ret, frame = self.camera.read()
        if ret:
            # Flip horizontally to mirror the image (like a mirror)
            frame = cv2.flip(frame, 1)
        return (ret, frame) if ret else None

    def release(self):
        """Release camera resources."""
        if self.camera is not None:
            self.camera.release()
            self.camera = None

    def __del__(self):
        """Cleanup on deletion."""
        self.release()
