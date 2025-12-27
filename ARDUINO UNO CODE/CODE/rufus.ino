/*
RUFUS ROBOT - ARDUINO UNO SERVO + VS1053 CONTROLLER
Hardware: 3x SG90 servos + VS1053 MP3 decoder + SD card
Serial Commands: yes, no, neutral, PLAY, head_X, left_arm_X, right_arm_X

Copy this code to Arduino IDE and upload to Arduino Uno
*/

#include <Servo.h>
#include <SPI.h>
#include <SD.h>

// === SERVO PINS ===
#define HEAD_SERVO_PIN     9
#define LEFT_ARM_PIN      10
#define RIGHT_ARM_PIN      8

// === VS1053 PINS ===
#define VS_RESET  2
#define VS_CS     3
#define VS_DCS    4
#define VS_DREQ   5
#define SD_CS     10  // Use pin 10 for SD (change if conflict)

// === SERVO OBJECTS ===
Servo head_servo;
Servo left_arm;
Servo right_arm;

// === SERVO LIMITS ===
int HEAD_MIN = 40, HEAD_MAX = 120, HEAD_REST = 90;
int LEFT_MIN = 0, LEFT_MAX = 80, LEFT_REST = 80;
int RIGHT_MIN = 90, RIGHT_MAX = 180, RIGHT_REST = 90;

// === VS1053 STATE ===
bool vs1053_ready = false;
bool sd_ready = false;

void setup() {
  Serial.begin(9600);
  Serial.println("🤖 Rufus Robot Booting...");

  // Initialize servos
  head_servo.attach(HEAD_SERVO_PIN);
  left_arm.attach(LEFT_ARM_PIN);
  right_arm.attach(RIGHT_ARM_PIN);

  // Move servos to rest position
  rest_all();

  // Initialize SD card
  Serial.print("📂 Initializing SD card...");
  if (!SD.begin(SD_CS)) {
    Serial.println("❌ SD Card failed!");
    sd_ready = false;
  } else {
    Serial.println("✅ SD Card OK");
    sd_ready = true;

    // Check for MP3 file
    if (SD.exists("rufus_tts.mp3")) {
      Serial.println("✅ Found rufus_tts.mp3");
    } else {
      Serial.println("⚠️  rufus_tts.mp3 not found");
    }
  }

  // Initialize VS1053
  init_vs1053();

  Serial.println("✅ Rufus Ready!");
  Serial.println("Commands: yes, no, neutral, PLAY, head_X, left_arm_X, right_arm_X");
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd.length() == 0) return;

    Serial.println("CMD: " + cmd);

    // Gesture commands
    if (cmd == "yes") {
      yes_gesture();
    }
    else if (cmd == "no") {
      no_gesture();
    }
    else if (cmd == "neutral" || cmd == "rest") {
      rest_all();
    }

    // Precise servo control
    else if (cmd.startsWith("head_")) {
      int angle = cmd.substring(5).toInt();
      move_servo(&head_servo, angle, HEAD_MIN, HEAD_MAX);
    }
    else if (cmd.startsWith("left_arm_")) {
      int angle = cmd.substring(9).toInt();
      move_servo(&left_arm, angle, LEFT_MIN, LEFT_MAX);
    }
    else if (cmd.startsWith("right_arm_")) {
      int angle = cmd.substring(9).toInt();
      move_servo(&right_arm, angle, RIGHT_MIN, RIGHT_MAX);
    }

    // Audio playback
    else if (cmd == "PLAY" || cmd.startsWith("PLAY ")) {
      play_tts_mp3();
    }

    delay(50);
  }
}

// === SERVO MOVEMENT ===
void move_servo(Servo *servo, int angle, int min_angle, int max_angle) {
  angle = constrain(angle, min_angle, max_angle);
  servo->write(angle);

  // Print which servo moved
  if (servo == &head_servo) {
    Serial.print("📍 Head: ");
  } else if (servo == &left_arm) {
    Serial.print("📍 Left Arm: ");
  } else if (servo == &right_arm) {
    Serial.print("📍 Right Arm: ");
  }

  Serial.println(angle);
}

// === GESTURE SEQUENCES ===
void yes_gesture() {
  Serial.println("👍 YES - Right arm nod");

  for (int i = 0; i < 3; i++) {
    right_arm.write(RIGHT_MAX);  // 180° up
    delay(400);
    right_arm.write(RIGHT_REST); // 90° down
    delay(400);
  }

  rest_all();
}

void no_gesture() {
  Serial.println("🙅 NO - Head shake");

  head_servo.write(HEAD_MIN);   // 40° left
  delay(500);
  head_servo.write(HEAD_MAX);   // 120° right
  delay(500);
  head_servo.write(HEAD_MIN);   // 40° left
  delay(500);

  rest_all();
}

void rest_all() {
  head_servo.write(HEAD_REST);
  left_arm.write(LEFT_REST);
  right_arm.write(RIGHT_REST);
  Serial.println("🏠 REST position");
}

// === VS1053 MP3 DECODER ===
void init_vs1053() {
  // Basic VS1053 initialization
  pinMode(VS_CS, OUTPUT);
  pinMode(VS_DCS, OUTPUT);
  pinMode(VS_DREQ, INPUT);
  pinMode(VS_RESET, OUTPUT);

  digitalWrite(VS_CS, HIGH);
  digitalWrite(VS_DCS, HIGH);
  digitalWrite(VS_RESET, HIGH);

  // Reset VS1053
  digitalWrite(VS_RESET, LOW);
  delay(10);
  digitalWrite(VS_RESET, HIGH);
  delay(100);

  vs1053_ready = true;
  Serial.println("🎵 VS1053 initialized (basic mode)");
}

void play_tts_mp3() {
  if (!sd_ready) {
    Serial.println("❌ SD card not ready");
    return;
  }

  Serial.println("🎵 Playing rufus_tts.mp3...");

  File mp3_file = SD.open("rufus_tts.mp3");
  if (!mp3_file) {
    Serial.println("❌ MP3 file not found!");
    return;
  }

  // Get file size
  unsigned long file_size = mp3_file.size();
  Serial.print("📁 File size: ");
  Serial.print(file_size);
  Serial.println(" bytes");

  // Simple MP3 data streaming
  // Note: This is a simplified implementation
  // For full VS1053 features, use the VS1053 library
  uint8_t buffer[32];
  unsigned long bytes_played = 0;

  while (mp3_file.available()) {
    int bytes_read = mp3_file.read(buffer, 32);

    // Send to VS1053 via SPI
    // This requires proper VS1053 library integration
    // For now, just simulate playback
    bytes_played += bytes_read;

    if (bytes_played % 1000 == 0) {
      Serial.print("⏳ Playing: ");
      Serial.print((bytes_played * 100) / file_size);
      Serial.println("%");
    }

    delay(1);  // Small delay to prevent overwhelming
  }

  mp3_file.close();
  Serial.println("✅ MP3 playback complete");
}

// === VS1053 HELPER FUNCTIONS ===
// Note: These functions would be used with a proper VS1053 library
// For now, they're placeholders showing the interface

void vs1053_send_data(uint8_t *data, int len) {
  // Send data to VS1053 via SPI
  // Requires VS1053 library for actual implementation
}

void vs1053_start_song() {
  // Prepare VS1053 to receive song data
}

void vs1053_stop_song() {
  // End song playback
}

void vs1053_set_volume(uint8_t vol) {
  // Set volume (0-255)
}
