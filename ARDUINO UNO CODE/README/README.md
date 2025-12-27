# ARDUINO UNO CODE - Rufus Robot

## What This Does

This Arduino sketch controls Rufus's hardware:
- **3x SG90 Servos** - Head, left arm, right arm movements
- **VS1053 MP3 Decoder** - Plays audio from SD card
- **Serial Communication** - Receives commands from Python via USB

## Features

✅ **Gesture Sequences** - Pre-programmed yes/no/rest gestures
✅ **Precise Servo Control** - Move any servo to specific angle
✅ **MP3 Playback** - Play rufus_tts.mp3 from SD card
✅ **Safe Limits** - Servo angles constrained to safe ranges
✅ **Serial Commands** - Easy command interface from Python

## Hardware

### Servos (3x SG90)
| Servo | Pin | Angle Range | Rest Position |
|-------|-----|-------------|---------------|
| Head | 9 | 40° - 120° | 90° |
| Left Arm | 10 | 0° - 80° | 80° |
| Right Arm | 8 | 90° - 180° | 90° |

### VS1053 MP3 Decoder
| Pin | Connection |
|-----|------------|
| 2 | VS_RESET |
| 3 | VS_CS |
| 4 | VS_DCS |
| 5 | VS_DREQ |
| 10 | SD_CS (SD card) |

### Power
- **5V 2A power supply** required for servos
- Don't power all 3 servos from Arduino 5V pin!

## Serial Commands

Send these commands via serial at 9600 baud:

### Gestures
- `yes` - Right arm nods 3 times
- `no` - Head shakes 2 times
- `neutral` or `rest` - All servos to rest position

### Precise Control
- `head_X` - Move head servo to angle X (40-120)
- `left_arm_X` - Move left arm to angle X (0-80)
- `right_arm_X` - Move right arm to angle X (90-180)

### Audio
- `PLAY` - Play rufus_tts.mp3 from SD card

## How to Upload

1. **Open Arduino IDE**
2. **Copy the code** from `CODE/rufus.ino`
3. **Select Board:** Arduino Uno
4. **Select Port:** Your Arduino's USB port
5. **Click Upload** (→ button)

## Wiring

### Servos
```
Arduino → Servo Signal Wire
Pin 8  → Right Arm Servo (orange/white)
Pin 9  → Head Servo (orange/white)
Pin 10 → Left Arm Servo (orange/white)
All servos: Red → 5V, Brown → GND
```

### VS1053
```
Arduino → VS1053
Pin 2 → VS_RESET
Pin 3 → VS_CS
Pin 4 → VS_DCS
Pin 5 → VS_DREQ
Pin 10 → SD_CS (SD card)
5V → VCC
GND → GND
```

## SD Card Setup

1. **Format SD card** as FAT32
2. **Create file:** `rufus_tts.mp3`
3. **Python will** write audio to this file
4. **Arduino plays** it when `PLAY` command sent

## Troubleshooting

**Servos not moving?**
- Check signal wire connections
- Verify 5V power supply connected
- Test with servo sweep example first

**SD card not detected?**
- Format as FAT32
- Check CS pin connection
- Try different SD card

**VS1053 not playing?**
- Verify rufus_tts.mp3 exists on SD card
- Check SPI pin connections
- VS1053 library may be needed for full features

**Serial commands not working?**
- Check baud rate is 9600
- Verify Arduino is connected to correct port
- Check Serial Monitor is set to "No line ending"

## File Description

- **rufus.ino** - Complete Arduino sketch (copy this to Arduino IDE)

## Notes

- VS1053 implementation is basic (placeholder for library integration)
- For full MP3 playback, consider using VS1053 library
- Servo movements include delays for smooth animation
- All angles constrained to safe ranges in code
