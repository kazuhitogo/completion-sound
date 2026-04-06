# completion-sound

[日本語版はこちら](README.ja.md)

A Python script that plays a pleasant chord sound on task completion.

Plays an **E–G–C chord** (ミソド / E4+G4+C5) in two hits — a short accent followed by a longer sustain — using a rich harmonic waveform (organ/bell hybrid with ADSR envelope).

No external dependencies — uses only the Python standard library.

## Platform support

| Platform | Player used |
|---|---|
| macOS | `afplay` (built-in) |
| Linux | `aplay` → `paplay` → `ffplay` (first found) |
| WSL | `powershell.exe` + `Media.SoundPlayer` |

## Sound design

- **Waveform:** sum of 8 partials (fundamental + harmonics up to 7th, +4 cent chorus, inharmonic bell partial)
- **Envelope:** ADSR (attack 12 ms / decay 60 ms / sustain 65% / release 120 ms)
- **Pattern:** 0.1 s chord → 50 ms silence → 0.8 s chord

## Requirements

- Python 3.8+
- A supported audio player (see table above — macOS and WSL have one built-in; Linux needs `aplay`, `paplay`, or `ffplay`)

## Usage

```bash
uv run complete_sound.py
# or
python3 complete_sound.py
```

Call it from any shell script, task runner, or hook system to get an audio notification when a long-running task finishes.

## Example: Claude Code hook

[Claude Code](https://claude.ai/code) supports [hooks](https://docs.anthropic.com/en/docs/claude-code/hooks) that run shell commands on specific events. To play this sound every time Claude finishes a response, add a `Stop` hook to `~/.claude/settings.json`:

### 1. Copy the script

```bash
mkdir -p ~/.claude/scripts
cp complete_sound.py ~/.claude/scripts/complete_sound.py
```

### 2. Add the hook

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "uv run ~/.claude/scripts/complete_sound.py",
            "timeout": 15
          }
        ]
      }
    ]
  }
}
```

## Customization

All timing and tuning lives in `generate()` and `make_note()`.

| What to change | Where | Example |
|---|---|---|
| Chord notes | `chord_freqs` in `generate()` | `[261.63, 329.63, 392.00]` for C–E–G |
| Hit durations | `make_chord(chord_freqs, 0.1)` / `0.8` | Change the float values |
| Gap between hits | `SAMPLE_RATE * 0.05` | Change `0.05` (seconds) |
| Harmonic richness | multipliers in `make_note()` | Reduce `0.55`, `0.28` … for a purer tone |
| Volume | `* 0.88` in `generate()` | Range 0.0–1.0 |

## License

MIT
