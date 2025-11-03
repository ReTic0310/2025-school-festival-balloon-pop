#!/usr/bin/env python3
"""
Generate 8-bit style sound effects for BALLOON SHOOTER.
"""

import numpy as np
import wave
import struct
from pathlib import Path


def generate_sine_wave(frequency, duration, sample_rate=44100, volume=0.3):
    """Generate a sine wave."""
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples)
    wave_data = volume * np.sin(2 * np.pi * frequency * t)
    return wave_data


def generate_square_wave(frequency, duration, sample_rate=44100, volume=0.3):
    """Generate a square wave (8-bit style)."""
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples)
    wave_data = volume * np.sign(np.sin(2 * np.pi * frequency * t))
    return wave_data


def generate_noise(duration, sample_rate=44100, volume=0.3):
    """Generate white noise."""
    samples = int(sample_rate * duration)
    wave_data = volume * np.random.uniform(-1, 1, samples)
    return wave_data


def apply_envelope(wave_data, attack=0.01, decay=0.05, sustain=0.7, release=0.1, sample_rate=44100):
    """Apply ADSR envelope to wave data."""
    total_samples = len(wave_data)
    attack_samples = int(attack * sample_rate)
    decay_samples = int(decay * sample_rate)
    release_samples = int(release * sample_rate)
    sustain_samples = total_samples - attack_samples - decay_samples - release_samples

    envelope = np.ones(total_samples)

    # Attack
    if attack_samples > 0:
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)

    # Decay
    if decay_samples > 0:
        envelope[attack_samples:attack_samples + decay_samples] = np.linspace(1, sustain, decay_samples)

    # Sustain
    envelope[attack_samples + decay_samples:attack_samples + decay_samples + sustain_samples] = sustain

    # Release
    if release_samples > 0:
        envelope[-release_samples:] = np.linspace(sustain, 0, release_samples)

    return wave_data * envelope


def save_wav(filename, wave_data, sample_rate=44100):
    """Save wave data as WAV file."""
    # Convert to 16-bit PCM
    wave_data = np.clip(wave_data, -1, 1)
    wave_data = (wave_data * 32767).astype(np.int16)

    # Write WAV file
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(wave_data.tobytes())

    print(f"Generated: {filename}")


def generate_shoot_sound():
    """Generate shooting sound effect."""
    # Short noise burst with decay
    duration = 0.15
    noise = generate_noise(duration, volume=0.4)
    envelope = np.linspace(1, 0, len(noise)) ** 2
    wave_data = noise * envelope
    return wave_data


def generate_pop_sound():
    """Generate balloon pop sound effect."""
    # Quick frequency drop (high to low)
    sample_rate = 44100
    duration = 0.2
    samples = int(sample_rate * duration)

    t = np.linspace(0, duration, samples)
    # Frequency drops from 800Hz to 100Hz
    frequency = 800 * np.exp(-10 * t)
    wave_data = 0.3 * np.sin(2 * np.pi * frequency * t)

    # Apply sharp decay envelope
    envelope = np.exp(-15 * t)
    wave_data = wave_data * envelope

    return wave_data


def generate_win_sound():
    """Generate victory/win sound effect."""
    # Ascending arpeggio (C-E-G-C)
    notes = [523, 659, 784, 1047]  # C5, E5, G5, C6
    note_duration = 0.15
    sample_rate = 44100

    wave_parts = []
    for freq in notes:
        note = generate_square_wave(freq, note_duration, sample_rate, volume=0.25)
        note = apply_envelope(note, attack=0.01, decay=0.05, sustain=0.8, release=0.05, sample_rate=sample_rate)
        wave_parts.append(note)

    wave_data = np.concatenate(wave_parts)
    return wave_data


def generate_lose_sound():
    """Generate game over/lose sound effect."""
    # Descending notes (sad trombone style)
    notes = [392, 349, 294, 262]  # G4, F4, D4, C4
    note_duration = 0.2
    sample_rate = 44100

    wave_parts = []
    for freq in notes:
        note = generate_square_wave(freq, note_duration, sample_rate, volume=0.25)
        note = apply_envelope(note, attack=0.01, decay=0.1, sustain=0.7, release=0.1, sample_rate=sample_rate)
        wave_parts.append(note)

    wave_data = np.concatenate(wave_parts)
    return wave_data


def main():
    """Generate all sound effects."""
    print("Generating 8-bit style sound effects...")
    print("=" * 50)

    output_dir = Path("assets/sounds")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate sounds
    shoot_sound = generate_shoot_sound()
    save_wav(str(output_dir / "shoot.wav"), shoot_sound)

    pop_sound = generate_pop_sound()
    save_wav(str(output_dir / "pop.wav"), pop_sound)

    win_sound = generate_win_sound()
    save_wav(str(output_dir / "win.wav"), win_sound)

    lose_sound = generate_lose_sound()
    save_wav(str(output_dir / "lose.wav"), lose_sound)

    print("=" * 50)
    print("All sound effects generated successfully!")


if __name__ == "__main__":
    main()
