# completion-sound

[English](README.md)

タスク完了時に心地よいコード音を鳴らす Python スクリプトです。

**ミソド（E4+G4+C5）の和音**を2回 — 短いアクセントのあとに長いサステイン — オルガン/ベルハイブリッドの波形と ADSR エンベロープで再生します。

外部依存なし。Python 標準ライブラリのみで動作します。

## 対応プラットフォーム

| プラットフォーム | 使用プレイヤー |
|---|---|
| macOS | `afplay`（OS 標準） |
| Linux | `aplay` → `paplay` → `ffplay`（見つかったもの順） |
| WSL | `powershell.exe` + `Media.SoundPlayer` |

## サウンドデザイン

- **波形:** 8つの倍音を合成（基音 + 7次倍音まで、+4セントコーラス、ベル的な非整数倍音）
- **エンベロープ:** ADSR（アタック 12ms / ディケイ 60ms / サステイン 65% / リリース 120ms）
- **パターン:** 0.1秒 → 50ms 無音 → 0.8秒

## 必要なもの

- Python 3.8+
- 対応オーディオプレイヤー（macOS・WSL は標準で内蔵。Linux は `aplay`・`paplay`・`ffplay` のいずれか）

## 使い方

```bash
uv run complete_sound.py
# または
python3 complete_sound.py
```

シェルスクリプト・タスクランナー・フックシステムなど、長時間タスクの完了通知として呼び出せます。

## 例: Claude Code のフックとして使う

[Claude Code](https://claude.ai/code) には、特定のイベントでシェルコマンドを実行する[フック機能](https://docs.anthropic.com/en/docs/claude-code/hooks)があります。Claude の応答が完了するたびにこの音を鳴らすには、`~/.claude/settings.json` に `Stop` フックを追加します。

### 1. スクリプトをコピー

```bash
mkdir -p ~/.claude/scripts
cp complete_sound.py ~/.claude/scripts/complete_sound.py
```

### 2. フックを追加

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

## カスタマイズ

タイミングや音程はすべて `generate()` と `make_note()` で変更できます。

| 変更したい内容 | 場所 | 例 |
|---|---|---|
| 和音の音程 | `generate()` の `chord_freqs` | `[261.63, 329.63, 392.00]` で C–E–G |
| 各ヒットの長さ | `make_chord(chord_freqs, 0.1)` / `0.8` | 数値を変更 |
| ヒット間の無音 | `SAMPLE_RATE * 0.05` | `0.05`（秒）を変更 |
| 倍音の豊かさ | `make_note()` 内の係数 | `0.55`・`0.28` などを下げると純音に近くなる |
| 音量 | `generate()` の `* 0.88` | 0.0〜1.0 の範囲で指定 |

## ライセンス

MIT
