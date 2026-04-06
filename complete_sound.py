#!/usr/bin/env python3
"""
Claude Code Stop hook: plays an E–G–C chord (E4+G4+C5) on task completion.
No external dependencies — uses only the Python standard library.

Supported platforms: macOS, Linux, WSL
"""
import math
import os
import struct
import subprocess
import sys
import tempfile
import wave

SAMPLE_RATE = 44100


def make_note(freq, duration, amplitude=0.55):
    n = int(SAMPLE_RATE * duration)
    attack  = 0.012
    decay   = 0.06
    sustain = 0.65
    release = 0.12

    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE

        # Harmonic series (organ/bell hybrid)
        s = (
            amplitude        * math.sin(2 * math.pi * freq        * t) +
            amplitude * 0.55 * math.sin(2 * math.pi * freq * 2    * t) +
            amplitude * 0.28 * math.sin(2 * math.pi * freq * 3    * t) +
            amplitude * 0.14 * math.sin(2 * math.pi * freq * 4    * t) +
            amplitude * 0.07 * math.sin(2 * math.pi * freq * 5    * t) +
            amplitude * 0.04 * math.sin(2 * math.pi * freq * 7    * t) +
            # Slight chorus: detune +4 cents
            amplitude * 0.18 * math.sin(2 * math.pi * freq * 1.0023 * t) +
            # Inharmonic bell partial
            amplitude * 0.06 * math.sin(2 * math.pi * freq * 2.756  * t)
        )

        # ADSR envelope
        if t < attack:
            env = t / attack
        elif t < attack + decay:
            env = 1.0 - (1.0 - sustain) * (t - attack) / decay
        elif t < duration - release:
            env = sustain
        else:
            env = sustain * max(0.0, (duration - t) / release)

        samples.append(s * env)

    return samples


def make_chord(freqs, duration, amplitude=0.3):
    """Mix multiple notes simultaneously into a chord."""
    n = int(SAMPLE_RATE * duration)
    chord = [0.0] * n
    for freq in freqs:
        note = make_note(freq, duration, amplitude)
        for i in range(n):
            chord[i] += note[i]
    return chord


def generate():
    # E4=ミ(329.63Hz)  G4=ソ(392.00Hz)  C5=ド(523.25Hz)
    chord_freqs = [329.63, 392.00, 523.25]

    all_samples = []
    all_samples.extend(make_chord(chord_freqs, 0.1))           # short hit
    all_samples.extend([0.0] * int(SAMPLE_RATE * 0.05))        # 50 ms gap
    all_samples.extend(make_chord(chord_freqs, 0.8))           # long sustain

    # Normalize to 88% to avoid clipping
    peak = max(abs(s) for s in all_samples)
    if peak > 0:
        all_samples = [s / peak * 0.88 for s in all_samples]

    return all_samples


def save_wav(samples, path):
    with wave.open(path, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SAMPLE_RATE)
        data = struct.pack(f'<{len(samples)}h',
                           *[int(s * 32767) for s in samples])
        f.writeframes(data)


def is_wsl():
    try:
        with open('/proc/version') as f:
            return 'microsoft' in f.read().lower()
    except FileNotFoundError:
        return False


def play_wav(path):
    if sys.platform == 'darwin':
        # macOS: afplay is built-in
        subprocess.run(['afplay', path], timeout=10)

    elif is_wsl():
        # WSL: hand off to Windows PowerShell
        win_path = subprocess.check_output(
            ['wslpath', '-w', path], text=True
        ).strip()
        subprocess.run([
            'powershell.exe', '-NoProfile', '-NonInteractive', '-c',
            f'(New-Object Media.SoundPlayer "{win_path}").PlaySync()'
        ], timeout=10)

    else:
        # Linux: try common players in order
        for cmd in (['aplay', path], ['paplay', path], ['ffplay', '-nodisp', '-autoexit', path]):
            if subprocess.run(['which', cmd[0]], capture_output=True).returncode == 0:
                subprocess.run(cmd, timeout=10)
                break


def main():
    samples = generate()

    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        tmp = f.name

    try:
        save_wav(samples, tmp)
        play_wav(tmp)
    finally:
        os.unlink(tmp)


if __name__ == '__main__':
    main()
