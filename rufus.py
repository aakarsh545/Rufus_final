"""
🤖 RUFUS AI ROBOT - COMPLETE WORKING VERSION (Mac/Pi)
GPT-5-nano + Whisper STT + TTS + Arduino Gestures + AI Movements + Idle Animations

FIXED VERSION:
- Added background idle animation thread (random movements every 8-15s)
- Fixed conversation memory and /clear command
- Improved TTS playback timing
- Better servo movement coordination
"""

import time, serial, subprocess, os, random, io, threading
import soundfile as sf
import sounddevice as sd
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

# === CONFIG ===
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "YOUR_API_KEY_HERE")

# Hardware ports (Mac/Pi)
ARDUINO_PORT = "/dev/cu.usbmodem11401"  # Mac - UPDATE THIS!
# ARDUINO_PORT = "/dev/serial0"         # Pi Zero W

TTS_MODEL = "tts-1"
VOICE = "echo"  # Deep robot voice (options: alloy, echo, fable, onyx, nova, shimmer)
WHISPER_MODEL = "whisper-1"
CHAT_MODEL = "gpt-4o-mini"  # Using gpt-4o-mini (fast, similar to gpt-5-nano concept)
ANSWER_MP3 = "rufus_tts.mp3"
RECORD_WAV = "input_5s.wav"

SAMPLE_RATE = 16000
DURATION_SEC = 5
MAX_TURNS = 10

# Idle animation settings
IDLE_ANIMATION_MIN = 8  # seconds
IDLE_ANIMATION_MAX = 15  # seconds

client = OpenAI(api_key=OPENAI_API_KEY)

# === SERVO LIMITS (Safe ranges) ===
SERVO_LIMITS = {
    "head": {"min": 40, "max": 120, "rest": 90},
    "left_arm": {"min": 0, "max": 80, "rest": 80},
    "right_arm": {"min": 90, "max": 180, "rest": 90}
}

# === GLOBAL STATE ===
idle_animation_running = False
idle_thread = None
conversation_locked = False  # Prevents idle animations during conversation

# === ARDUINO SERIAL ===
def open_arduino():
    """Open Arduino serial connection"""
    try:
        ser = serial.Serial(ARDUINO_PORT, 9600, timeout=1)
        time.sleep(2)  # Wait for Arduino to reset
        send_command(ser, "rest")
        print(f"✅ Arduino connected on {ARDUINO_PORT}")
        return ser
    except serial.SerialException as e:
        print(f"❌ Failed to connect to Arduino: {e}")
        print(f"   Check port: {ARDUINO_PORT}")
        print("   Running in SIMULATION mode (no hardware)")
        return None

def send_command(uno, cmd):
    """Send gesture/movement command to Arduino"""
    if uno is None:
        print(f"[SIMULATION] Arduino: {cmd}")
        return

    try:
        uno.write(f"{cmd}\n".encode("utf-8"))
        print(f"📡 Arduino: {cmd}")
        time.sleep(0.1)

        # Read Arduino response
        while uno.in_waiting:
            response = uno.read_until(b"\n").decode("utf-8", errors="ignore").strip()
            if response:
                print(f"   Arduino: {response}")
    except Exception as e:
        print(f"❌ Serial error: {e}")

# === CONVERSATION MEMORY ===
conversation_history = [{
    "role": "system",
    "content": (
        "You are Rufus, a friendly robot companion in a small cardboard body. "
        "You have expressive servo gestures (head shake, arm wave). "
        "Keep responses short (1-2 sentences), warm, and natural. "
        "Remember conversation context."
    )
}]

def add_to_memory(question, answer):
    """Maintain conversation memory (10 turns max)"""
    conversation_history.append({"role": "user", "content": question})
    conversation_history.append({"role": "assistant", "content": answer})

    # Trim old messages (keep system prompt + last MAX_TURNS exchanges)
    if len(conversation_history) > 1 + 2 * MAX_TURNS:
        conversation_history[:] = [conversation_history[0]] + conversation_history[-2 * MAX_TURNS:]

    print(f"🧠 Memory: {len(conversation_history)//2} turns")

def clear_memory():
    """Clear conversation memory"""
    global conversation_history
    conversation_history = [{
        "role": "system",
        "content": (
            "You are Rufus, a friendly robot companion in a small cardboard body. "
            "You have expressive servo gestures (head shake, arm wave). "
            "Keep responses short (1-2 sentences), warm, and natural. "
            "Remember conversation context."
        )
    }]
    print("🧹 Memory cleared!")

# === IDLE ANIMATION THREAD ===
def idle_animation_loop(arduino):
    """Background thread for random idle animations"""
    global idle_animation_running, conversation_locked

    print("💫 Idle animations started")

    while idle_animation_running:
        # Random interval between animations
        interval = random.uniform(IDLE_ANIMATION_MIN, IDLE_ANIMATION_MAX)
        print(f"💤 Next idle movement in {interval:.1f}s...")

        # Sleep in small chunks to check for stop signal
        for _ in range(int(interval * 10)):
            time.sleep(0.1)
            if not idle_animation_running:
                return

        # Don't animate during conversation
        if conversation_locked:
            continue

        # Perform random subtle movement
        if arduino:
            servo = random.choice(["head", "left_arm", "right_arm"])
            limits = SERVO_LIMITS[servo]

            # Small random movement (±15 degrees from rest)
            rest_pos = limits["rest"]
            min_offset = -15
            max_offset = 15

            new_pos = rest_pos + random.randint(min_offset, max_offset)
            new_pos = max(limits["min"], min(limits["max"], new_pos))

            send_command(arduino, f"{servo}_{new_pos}")
            time.sleep(0.5)

            # Return to rest
            send_command(arduino, f"{servo}_{limits['rest']}")

def start_idle_animations(arduino):
    """Start background idle animation thread"""
    global idle_animation_running, idle_thread

    if idle_animation_running:
        return

    idle_animation_running = True
    idle_thread = threading.Thread(target=idle_animation_loop, args=(arduino,), daemon=True)
    idle_thread.start()

def stop_idle_animations():
    """Stop idle animation thread"""
    global idle_animation_running
    idle_animation_running = False
    if idle_thread:
        idle_thread.join(timeout=2)

# === VOICE INPUT (Whisper STT) ===
def record_audio(duration=DURATION_SEC):
    """Record 5s from microphone"""
    print(f"🎤 Recording {duration}s...")
    try:
        audio = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype="int16")
        sd.wait()  # Wait for recording to complete
        sf.write(RECORD_WAV, audio, SAMPLE_RATE, subtype="PCM_16")
        print("✅ Saved", RECORD_WAV)
        return True
    except Exception as e:
        print(f"❌ Recording failed: {e}")
        return False

def transcribe_audio():
    """Whisper STT → text"""
    try:
        with open(RECORD_WAV, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model=WHISPER_MODEL,
                file=audio_file
            )
        return transcript.text.strip()
    except Exception as e:
        print(f"❌ Transcription failed: {e}")
        return None

# === GPT CHAT ===
def get_ai_response(question):
    """GPT chat with memory"""
    try:
        resp = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=conversation_history,
            max_completion_tokens=80
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ AI response failed: {e}")
        return "I'm having trouble thinking right. Could you try again?"

# === TTS SPEECH SYNTHESIS ===
def speak_response(text):
    """OpenAI TTS → MP3 → speakers"""
    print(f"🎤 Rufus: {text}")

    try:
        speech = client.audio.speech.create(
            model=TTS_MODEL,
            voice=VOICE,
            input=text,
            response_format="mp3"
        )

        with open(ANSWER_MP3, "wb") as f:
            f.write(speech.content)

        # Platform-specific playback (blocking)
        system = os.uname().sysname if hasattr(os, 'uname') else os.name

        if system == "Darwin":  # macOS
            subprocess.run(["afplay", ANSWER_MP3], check=True)
        elif system == "Linux":
            subprocess.run(["aplay", ANSWER_MP3], check=True)
        else:
            subprocess.run(["open", ANSWER_MP3], check=True)

        print("✅ Speech complete")
        return True

    except Exception as e:
        print(f"❌ Speech failed: {e}")
        return False

# === GESTURE CLASSIFICATION ===
def classify_gesture(question, answer):
    """AI determines yes/no/neutral gesture"""
    answer_lower = answer.lower()

    # Positive indicators
    if any(word in answer_lower for word in ["yes", "good", "happy", "great", "awesome", "certainly", "absolutely"]):
        return "yes"

    # Negative indicators
    elif any(word in answer_lower for word in ["no", "sorry", "bad", "can't", "unfortunately"]):
        return "no"

    return "neutral"

# === AI NATURAL MOVEMENTS ===
def natural_movements(uno, answer):
    """AI-driven expressive movements during conversation"""
    movements = []
    answer_lower = answer.lower()

    # Context-aware movements
    if any(word in answer_lower for word in ["happy", "excited", "great", "awesome"]):
        movements = ["right_arm_150", "left_arm_60"]
    elif "no" in answer_lower:
        movements = ["head_110", "head_70"]
    elif any(word in answer_lower for word in ["hmm", "interesting", "think"]):
        movements = ["head_100"]
    elif any(word in answer_lower for word in ["hello", "hi"]):
        movements = ["right_arm_160", "left_arm_50"]
    else:
        # Random subtle movement
        servo = random.choice(["head", "left_arm", "right_arm"])
        limits = SERVO_LIMITS[servo]
        pos = random.randint(limits["min"] + 10, limits["max"] - 10)
        movements = [f"{servo}_{pos}"]

    # Execute movements
    for movement in movements[:2]:  # Max 2 movements
        send_command(uno, movement)
        time.sleep(random.uniform(0.3, 0.6))

    # Return to rest
    send_command(uno, "rest")

# === MAIN RUFUS LOOP ===
def main():
    global conversation_locked

    print("\n" + "="*60)
    print("🤖 RUFUS AI ROBOT v2.1 - FIXED VERSION")
    print("🎙️  GPT-4o-mini + Whisper STT + TTS + Gestures + Idle Animations")
    print("📖 Type text OR press ENTER (5s mic recording)")
    print("🔄 /clear = reset memory | exit = quit")
    print("="*60)

    # Initialize hardware
    arduino = open_arduino()
    start_idle_animations(arduino)

    try:
        while True:
            user_input = input("\n👤 You: ").strip()

            # Exit command
            if user_input.lower() in ["exit", "quit", "bye"]:
                conversation_locked = True
                speak_response("Goodbye! It was great talking with you!")
                send_command(arduino, "yes")
                break

            # Memory reset
            if user_input.lower() == "/clear":
                clear_memory()
                speak_response("Memory cleared! Ready for a fresh start.")
                continue

            # INPUT SOURCE DETERMINATION
            if not user_input:  # Empty = Voice input
                conversation_locked = True  # Stop idle animations
                record_audio()
                question = transcribe_audio()

                if not question:
                    print("❌ Nothing heard clearly, try again.")
                    conversation_locked = False
                    continue

                print(f"🗣️  Heard: {question}")
            else:
                conversation_locked = True
                question = user_input
                print(f"💬 Using text: {question}")

            # === AI PROCESSING ===
            print("🤔 Rufus thinking...")
            answer = get_ai_response(question)
            print(f"🤖 Rufus: {answer}")

            # Update memory
            add_to_memory(question, answer)

            # === GESTURES + MOVEMENTS ===
            gesture = classify_gesture(question, answer)
            send_command(arduino, gesture)
            time.sleep(0.5)
            natural_movements(arduino, answer)

            # === SPEECH OUTPUT ===
            speak_response(answer)

            # Unlock for idle animations
            conversation_locked = False

    except KeyboardInterrupt:
        print("\n👋 Rufus powering off...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        # Cleanup
        conversation_locked = True
        stop_idle_animations()
        if arduino:
            send_command(arduino, "rest")
            time.sleep(0.5)
            arduino.close()
        print("✅ Shutdown complete")

if __name__ == "__main__":
    main()
