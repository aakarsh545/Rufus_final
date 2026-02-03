#!/usr/bin/env python3
"""
Rufus Pi API Server
Receives commands from web interface (Vercel) via WiFi
Controls Arduino servos, gestures, and TTS
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import serial
import time
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
import pygame
import tempfile
import sounddevice as sd
import soundfile as sf

app = Flask(__name__)
CORS(app)  # Allow requests from Vercel

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# AI Settings
CHAT_MODEL = "gpt-4o-mini"
TTS_MODEL = "tts-1"
VOICE = "onyx"
MAX_TURNS = 10

# Audio recording settings
SAMPLE_RATE = 16000
DURATION_SEC = 5
RECORD_WAV = "temp_recording.wav"

# System prompt for GPT-4o-mini
SYSTEM_PROMPT = """You are Rufus, a friendly, playful AI robot companion with a physical body.

IMPORTANT: You must respond with valid JSON in this exact format:
{
  "speech": "your full conversational response (detailed, friendly, 2-4 sentences)",
  "gesture": "yes|no|neutral"
}

GESTURE RULES:
- Analyze the USER'S INPUT and summarize it to: YES, NO, or NEUTRAL
- "yes" = User said something positive, agreeing, asking "yes" questions, greeting
- "no" = User said something negative, disagreeing, asking "no" questions
- "neutral" = Everything else (questions, statements, confusion, etc.)

Give FULL, detailed responses:
- Explain things thoroughly
- Be conversational and friendly
- Don't be too brief - expand on your answers
- Show enthusiasm and personality
- Use 2-4 sentences typically, more if needed

Examples:
User: "Hello!" → {"speech": "Well hello there! It's absolutely wonderful to see you! I'm Rufus, your friendly AI robot companion, and I'm really excited we get to chat today. How can I help you?", "gesture": "yes"}

User: "Are you a robot?" → {"speech": "I sure am! I'm Rufus, a friendly AI robot companion made with cardboard and servos. I love having conversations and helping out however I can. It's pretty cool being a robot!", "gesture": "neutral"}

Be warm, friendly, and give thorough, detailed answers!"""

# Conversation memory
conversation_history = []

# Arduino serial setup
ARDUINO_PORT = "/dev/ttyACM0"
ARDUINO_BAUD = 9600
arduino = None

# Audio setup
pygame.mixer.init(frequency=24000, size=-16, channels=1, buffer=512)

# Servo pin assignments
SERVO_PINS = {
    "pan": 2,
    "left_arm": 4,
    "right_arm": 5
}

# Gesture sequences
GESTURES = {
    "wave": [
        ("pan", 90), ("right_arm", 70), ("right_arm", 40),
        ("right_arm", 70), ("right_arm", 40), ("right_arm", 70),
        ("right_arm", 40), ("left_arm", 90), ("right_arm", 90)
    ],
    "nod": [
        ("pan", 105), ("pan", 75), ("pan", 105), ("pan", 75), ("pan", 90)
    ],
    "shake": [
        ("pan", 65), ("pan", 115), ("pan", 65), ("pan", 115), ("pan", 90)
    ],
    "happy": [
        ("left_arm", 170), ("right_arm", 170), ("pan", 75),
        ("pan", 105), ("pan", 75), ("pan", 105),
        ("left_arm", 90), ("right_arm", 90), ("pan", 90)
    ],
    "sad": [
        ("pan", 50), ("left_arm", 60), ("right_arm", 60),
        ("pan", 50), ("left_arm", 90), ("right_arm", 90), ("pan", 90)
    ],
    "excited": [
        ("left_arm", 170), ("right_arm", 170), ("pan", 60),
        ("pan", 120), ("left_arm", 90), ("right_arm", 90), ("pan", 90)
    ],
    "curious": [
        ("pan", 70), ("left_arm", 110), ("right_arm", 110),
        ("pan", 70), ("left_arm", 90), ("right_arm", 90), ("pan", 90)
    ],
    "rest": [
        ("pan", 90), ("left_arm", 90), ("right_arm", 90)
    ]
}

def init_arduino():
    """Initialize Arduino connection"""
    global arduino
    try:
        arduino = serial.Serial(ARDUINO_PORT, ARDUINO_BAUD, timeout=1)
        time.sleep(2)  # Wait for Arduino to reset and send READY

        # Read all available data and look for READY
        ready = False
        start_time = time.time()
        while time.time() - start_time < 3:  # Wait up to 3 seconds
            if arduino.in_waiting > 0:
                response = arduino.readline().decode('utf-8').strip()
                print(f"📩 Arduino says: {response}")
                if response == "READY":
                    ready = True
                    break
            time.sleep(0.1)

        if ready:
            print("✅ Arduino connected successfully!")
            return True
        else:
            print("⚠️  Arduino connected but didn't receive READY signal")
            print("   Servo commands may not work properly")
            return True  # Still continue anyway
    except Exception as e:
        print(f"❌ Arduino not connected: {e}")
        print("   Servo control will not work")
        arduino = None
        return False

def send_servo_command(pin, angle):
    """Send servo command to Arduino"""
    global arduino
    if not arduino or not arduino.is_open:
        print(f"❌ Arduino not connected - cannot send command to pin {pin}")
        return False
    try:
        command = f"{pin}:{angle}\n"
        print(f"📤 Sending: {command.strip()}")
        arduino.write(command.encode('utf-8'))
        time.sleep(0.05)

        # Read acknowledgment
        if arduino.in_waiting > 0:
            ack = arduino.readline().decode('utf-8').strip()
            print(f"📥 Arduino ACK: {ack}")
            return ack.startswith("OK")
        else:
            print("⚠️  No acknowledgment from Arduino")
            return True  # Assume it worked anyway
    except Exception as e:
        print(f"❌ Servo command failed: {e}")
        return False

def perform_gesture(gesture_name):
    """Execute a gesture sequence"""
    if gesture_name not in GESTURES:
        return False

    sequence = GESTURES[gesture_name]
    for servo, angle in sequence:
        pin = SERVO_PINS.get(servo)
        if pin:
            send_servo_command(pin, angle)
            time.sleep(0.15)
    return True

def speak_text(text):
    """Convert text to speech and play"""
    try:
        response = client.audio.speech.create(
            model=TTS_MODEL,
            voice=VOICE,
            input=text,
            response_format="wav"
        )

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_file = f.name
            f.write(response.content)

        sound = pygame.mixer.Sound(temp_file)
        sound.play()
        pygame.time.wait(int(sound.get_length() * 1000))

        os.unlink(temp_file)
        return True
    except Exception as e:
        print(f"❌ TTS failed: {e}")
        return False

def add_to_memory(role, content):
    """Add message to conversation memory"""
    conversation_history.append({"role": role, "content": content})
    # Keep only last MAX_TURNS exchanges
    if len(conversation_history) > MAX_TURNS * 2 + 1:
        conversation_history[:] = conversation_history[-(MAX_TURNS * 2 + 1):]

def get_ai_response(user_message):
    """Get response from GPT-4o-mini with structured output"""
    print(f"\n🧠 User: {user_message}")

    add_to_memory("user", user_message)

    # Build messages with system prompt
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history

    try:
        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=messages,
            max_tokens=500,
            temperature=0.8,
            response_format={"type": "json_object"}
        )

        response_text = response.choices[0].message.content.strip()

        # Parse JSON response
        response_data = json.loads(response_text)

        speech = response_data.get("speech", "")
        gesture = response_data.get("gesture", "neutral")

        # Add AI's speech to memory
        add_to_memory("assistant", speech)

        print(f"🤖 Rufus: {speech}")
        print(f"⚙️  Gesture: {gesture}")

        return speech, gesture

    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse AI's JSON: {e}")
        return "I'm having trouble processing that right now.", "neutral"

    except Exception as e:
        print(f"❌ OpenAI API failed: {e}")
        return "Something went wrong. Can you try again?", "neutral"

def execute_gesture(gesture):
    """Execute gesture (yes/nod, no/shake, neutral/rest)"""
    if not gesture or gesture == "neutral":
        perform_gesture("rest")
    elif gesture == "yes":
        perform_gesture("nod")
    elif gesture == "no":
        perform_gesture("shake")

# ==================== API ENDPOINTS ====================

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'arduino_connected': arduino is not None})

@app.route('/api/servo', methods=['POST'])
def control_servo():
    """Control individual servo"""
    data = request.json
    servo = data.get('servo')
    angle = data.get('angle')

    pin = SERVO_PINS.get(servo)
    if not pin:
        return jsonify({'success': False, 'error': 'Unknown servo'})

    success = send_servo_command(pin, angle)
    return jsonify({'success': success})

@app.route('/api/gesture', methods=['POST'])
def trigger_gesture():
    """Trigger a gesture"""
    data = request.json
    gesture = data.get('gesture')

    success = perform_gesture(gesture)
    return jsonify({'success': success})

@app.route('/api/speak', methods=['POST'])
def text_to_speech():
    """Convert text to speech"""
    data = request.json
    text = data.get('text')

    if not text:
        return jsonify({'success': False, 'error': 'No text provided'})

    success = speak_text(text)
    return jsonify({'success': success})

@app.route('/api/chat', methods=['POST'])
def chat():
    """AI chat with gesture and TTS"""
    data = request.json
    user_message = data.get('message')

    if not user_message:
        return jsonify({'success': False, 'error': 'No message provided'})

    # Get AI response
    response_text, gesture = get_ai_response(user_message)

    # Execute gesture
    execute_gesture(gesture)

    # Speak the response
    speak_text(response_text)

    # Map gesture for web interface
    gesture_map = {
        "yes": "nod",
        "no": "shake",
        "neutral": "rest"
    }

    return jsonify({
        'success': True,
        'response': response_text,
        'gesture': gesture_map.get(gesture, "rest")
    })

@app.route('/api/voice-chat', methods=['POST'])
def voice_chat():
    """Full voice conversation: Record → STT → AI → TTS → Play (records on Pi)"""
    print(f"\n🎤 Recording for {DURATION_SEC} seconds...")

    try:
        # Record audio locally on Pi
        recording = sd.rec(
            int(DURATION_SEC * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="int16"
        )
        sd.wait()  # Wait for recording to complete

        # Save to temp file
        sf.write(RECORD_WAV, recording, SAMPLE_RATE)
        print("✅ Recording complete")

        # Transcribe with Whisper
        print("📝 Transcribing...")
        with open(RECORD_WAV, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=f
            )
        user_text = transcript.text.strip()
        print(f"✅ You said: '{user_text}'")

        # Clean up temp file
        os.unlink(RECORD_WAV)

        if not user_text:
            return jsonify({'success': False, 'error': 'No speech detected'})

        # Get AI response
        response_text, gesture = get_ai_response(user_text)

        # Execute gesture
        execute_gesture(gesture)

        # Speak the response
        speak_text(response_text)

        # Map gesture for web interface
        gesture_map = {
            "yes": "nod",
            "no": "shake",
            "neutral": "rest"
        }

        return jsonify({
            'success': True,
            'transcript': user_text,
            'response': response_text,
            'gesture': gesture_map.get(gesture, "rest")
        })

    except Exception as e:
        # Clean up temp file on error
        if os.path.exists(RECORD_WAV):
            os.unlink(RECORD_WAV)
        print(f"❌ Voice chat failed: {e}")
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("🌐 Rufus Pi API Server")
    init_arduino()
    print("✅ Server running on http://0.0.0.0:5001")
    print("📡 Ready to receive commands from Vercel!")
    app.run(host='0.0.0.0', port=5001, debug=False)
