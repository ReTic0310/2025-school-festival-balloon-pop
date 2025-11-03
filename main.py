#!/usr/bin/env python3
"""
HEART BALLOON POP - Main entry point.

A game where players shoot balloons by making heart gestures with their hands.
"""

import sys
import time
import pygame
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from camera_manager import CameraManager
from heart_detector import HeartDetector
from game import Game


def main():
    """Main game loop."""
    print("=" * 50)
    print("HEART BALLOON POP")
    print("=" * 50)

    # Initialize camera
    print("\nInitializing camera...")
    camera_manager = CameraManager("camera_config.json")

    if not camera_manager.initialize():
        print("ERROR: Failed to initialize camera")
        print("Please check if the camera is connected")
        return 1

    # Initialize heart detector
    print("Initializing heart detector...")
    heart_detector = HeartDetector()

    # Initialize game
    print("Initializing game...")
    game = Game()

    print("\nGame ready!")
    print("Make a gun gesture with your hand to shoot balloons!")
    print("- Point horizontally to aim (reticle appears)")
    print("- Point up to shoot!")
    print("Press ESC or Q to quit")
    print("=" * 50)

    # Main loop
    last_time = time.time()
    last_heart_state = False
    last_aiming_position = None  # Store last aiming position for shooting

    try:
        while game.running:
            # Calculate delta time
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time

            # Cap delta time to avoid huge jumps
            if dt > 0.1:
                dt = 0.1

            # Read camera frame
            frame_data = camera_manager.read_frame()

            if frame_data:
                ret, frame = frame_data

                # Detect heart gesture and get debug frame with landmarks
                heart_detected, heart_position, is_aiming, aiming_position, debug_frame = heart_detector.detect(frame)

                # Pass debug frame (with landmarks) to game for preview
                game.set_camera_frame(debug_frame if debug_frame is not None else frame)

                # Update aiming state in game (allow in READY and RUN states)
                if game.state in ["READY", "RUN"]:
                    game.set_aiming(is_aiming, aiming_position)
                    # Store aiming position for shooting
                    if is_aiming and aiming_position:
                        last_aiming_position = aiming_position

                # Shoot on heart gesture (rising edge detection)
                if heart_detected and not last_heart_state:
                    if game.state == "RUN":
                        # Use last aiming position instead of current position
                        if last_aiming_position:
                            x, y = last_aiming_position
                            game.shoot(x, y)

                last_heart_state = heart_detected

            # Handle pygame events
            for event in pygame.event.get():
                command = game.handle_event(event)

                if command == "start":
                    game.start_game()
                    print("\nGame started!")

                elif command == "manual_shoot":
                    # Manual shoot at center (for testing)
                    game.shoot(500, 500)

                elif command == "save_screenshot":
                    filename = game.save_result_screenshot()
                    print(f"\nScreenshot saved: {filename}")

            # Run game frame
            game.run_frame(dt)

            # Cap frame rate
            game.clock.tick(60)

    except KeyboardInterrupt:
        print("\nGame interrupted by user")

    finally:
        # Cleanup
        print("\nCleaning up...")
        camera_manager.release()
        heart_detector.release()
        game.quit()
        print("Goodbye!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
