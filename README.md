# 🤖 Rufus AI Robot Companion

A physical AI robot with voice conversation, expressive gestures, and idle animations.

## Quick Start

```bash
# Install dependencies
pip install -r python/requirements.txt

# Set up environment
cp python/.env.example .env
# Edit .env with your OPENAI_API_KEY

# Run Rufus
cd python
python main.py
```

## Project Structure

```
rufus/
├── python/              # Python code (Mac/Pi)
│   ├── rufus.py        # Main robot code
│   ├── main.py         # Entry point
│   ├── requirements.txt
│   └── .env.example
├── arduino_uno/        # Arduino Uno firmware
│   └── rufus.ino
├── esp32/              # ESP32 code (future)
└── docs/               # Documentation
```

## Features

- 🎤 Voice input (Whisper STT)
- 🗣️ Speech output (OpenAI TTS)
- 🤖 Expressive gestures (3 servos)
- 💫 Idle animations (random movements)
- 🧠 Conversation memory (10 turns)
- 🎭 AI-driven movements

## Hardware

- Arduino Uno R3
- 3x SG90 servos
- VS1053 MP3 decoder
- INMP441 microphone (ESP32 - future)

## Commands

- `text` - Type message
- `press ENTER` - Voice input (5s)
- `/clear` - Reset memory
- `exit` - Quit

## Version

**v2.1** - Fixed idle animations, memory system, and TTS timing
