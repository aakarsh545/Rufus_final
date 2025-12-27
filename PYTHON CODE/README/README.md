# PYTHON CODE - Rufus AI Robot

## What This Does

This Python code runs Rufus's AI brain on your Mac or Raspberry Pi. It connects to:

- **OpenAI GPT-4o-mini** - For conversation and responses
- **Whisper STT** - Speech-to-text (converts your voice to text)
- **OpenAI TTS** - Text-to-speech (converts responses to voice)
- **Arduino Uno** - Controls servos for gestures and movements

## Features

✅ **Voice Input** - Press ENTER to record 5 seconds of audio
✅ **Text Input** - Type messages directly
✅ **Conversation Memory** - Remembers last 10 turns of conversation
✅ **Smart Gestures** - AI classifies responses as yes/no/neutral
✅ **Natural Movements** - Context-aware servo movements
✅ **Idle Animations** - Random subtle movements every 8-15 seconds
✅ **Memory Clear** - Type `/clear` to reset conversation

## Requirements

- Python 3.9+
- OpenAI API key
- Arduino Uno connected via USB
- Microphone (for voice input)

## How to Run

1. **Install dependencies:**
   ```bash
   pip install openai==1.35.0 pyserial==3.5 sounddevice==0.4.7 soundfile==0.12.1 numpy==1.24.3 python-dotenv==1.0.0
   ```

2. **Set up API key:**
   - Create a `.env` file in the same folder as the code
   - Add: `OPENAI_API_KEY=your-api-key-here`

3. **Update Arduino port** (line 21 in code):
   - Mac: `/dev/cu.usbmodemXXXX` (find with `ls /dev/cu.*`)
   - Pi: `/dev/serial0`

4. **Run:**
   ```bash
   python rufus.py
   ```

## Commands

- `text here` - Type message
- `press ENTER` - Voice input (records 5 seconds)
- `/clear` - Reset conversation memory
- `exit` - Quit program

## Hardware Connection

Connects to Arduino Uno via USB serial at 9600 baud to control:
- Head servo (pin 9) - 40° to 120°
- Left arm servo (pin 10) - 0° to 80°
- Right arm servo (pin 8) - 90° to 180°

## Troubleshooting

**Arduino not connecting?**
- Check port is correct: `ls /dev/cu.*` (Mac) or `ls /dev/tty*` (Pi)
- Arduino runs in simulation mode if not connected

**Microphone not working?**
- Check mic permissions in System Settings
- Ensure mic is selected as input device

**OpenAI API errors?**
- Verify API key is set correctly
- Check you have API credits available

## File Description

- **rufus.py** - Main robot code (copy this to run)
- **requirements.txt** - All Python dependencies
- **.env.example** - Environment variables template
