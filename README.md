# 🤖 Rufus AI Robot Companion

A physical AI robot with voice conversation, expressive gestures, and idle animations.

## Quick Start

1. **Arduino Setup:**
   - Open `ARDUINO UNO CODE/CODE/rufus.ino`
   - Upload to Arduino Uno

2. **Python Setup:**
   ```bash
   cd "PYTHON CODE/CODE"
   pip install -r requirements.txt

   # Create .env file
   echo "OPENAI_API_KEY=your-key-here" > .env
   echo "ARDUINO_PORT=/dev/cu.usbmodemXXXX" >> .env

   # Run Rufus
   python rufus.py
   ```

## Project Structure

```
rufus/
├── PYTHON CODE/
│   ├── README/           # Documentation
│   │   └── README.md
│   └── CODE/             # Copy-paste ready code
│       ├── rufus.py      # Main robot code
│       ├── requirements.txt
│       └── .env.example
│
├── ARDUINO UNO CODE/
│   ├── README/           # Documentation
│   │   └── README.md
│   └── CODE/             # Copy-paste ready code
│       └── rufus.ino     # Arduino sketch
│
└── README.md             # This file
```

## Features

- 🎤 **Voice Input** - Whisper STT (5s recording)
- 🗣️ **Speech Output** - OpenAI TTS (echo voice)
- 🤖 **Smart Gestures** - Yes/no/rest + natural movements
- 💫 **Idle Animations** - Random movements every 8-15s
- 🧠 **Conversation Memory** - Remembers last 10 turns
- 🎭 **AI-Driven Movements** - Context-aware servo control

## Hardware

- Arduino Uno R3
- 3x SG90 servos (head, left arm, right arm)
- VS1053 MP3 decoder + SD card
- INMP441 microphone (future ESP32 integration)

## Commands

- `text here` - Type message
- `press ENTER` - Voice input (5s recording)
- `/clear` - Reset conversation memory
- `exit` - Quit program

## Version

**v2.1** - Fixed idle animations, memory system, and TTS timing

Full documentation in each folder's README.
