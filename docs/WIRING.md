# Rufus Robot - Wiring Guide

Complete wiring diagrams and instructions for Rufus hardware.

## Components Overview

### Controller Board
- **Arduino Uno R3** (ATmega328P)
- USB connection for power and serial communication
- Operating voltage: 5V

### Servo Motors (3x SG90)
| Servo     | Function     | Pin  | Wire Color    |
|-----------|-------------|------|---------------|
| Head      | Pan movement | 9    | Orange (signal) |
| Left Arm  | Arm up/down  | 10   | Orange (signal) |
| Right Arm | Arm up/down  | 8    | Orange (signal) |

**SG90 Servo Wire Colors:**
- **Orange/White** - Signal
- **Red** - VCC (+5V)
- **Brown/Black** - GND

### Audio System
- **VS1053 MP3 Decoder**
- **MicroSD Card** for audio storage
- **3.5mm audio jack** or speaker output

### Microphone (Future)
- **INMP441 I2S Microphone**
- Will connect to ESP32 for standalone mode

---

## Wiring Diagrams

### Arduino Uno Pin Map

```
┌─────────────────────────────────────┐
│         ARDUINO UNO R3              │
│                                     │
│  [USB]                          [ ] │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ POWER                       │   │
│  │ 3.3V [] 5V [] GND [] VIN    │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ DIGITAL (PWM~)              │   │
│  │ 13 [] 12 [] 11 [] 10 [] 9 [] │   │  → Servo connections
│  │ 8 []  7 []  6 []  5 []  4 [] │   │
│  │ 3 []  2 []  1 []  0 []      │   │  → VS1053 RX/TX
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ ANALOG IN                   │   │
│  │ A0 [] A1 [] A2 [] A3 []     │   │
│  │ A4 [] A5 []                 │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

### Servo Wiring

```
                  ┌──────────┐
POWER: 5V --------┤  VCC     │
                  │          │
GND   ------------┤  GND     │
                  │   SG90   │
SIGNAL (Pin 9) ---┤  SIGNAL  │
                  └──────────┘
                    HEAD SERVO

Repeat for LEFT_ARM (Pin 10) and RIGHT_ARM (Pin 8)
```

### Complete Wiring Schematic

```
                        ARDUINO UNO
                    ┌──────────────────┐
                    │                  │
   Servo Signal  ---│ D8  D9  D10      │--- Servo Signals
   (Right,Head,Left)│                  │
                    │             D2   │--- RX → VS1053 TX
                    │             D3   │--- TX → VS1053 RX
                    │                  │
      5V ---------  │ 5V               │--- Servo VCC (all 3)
                    │                  │
      GND --------  │ GND              │--- Servo GND (all 3)
                    │                  │--- VS1053 GND
                    └──────────────────┘
                          │
                          │ USB
                          │
                      Computer
```

### VS1053 Wiring (Simplified)

```
ARDUINO          VS1053 BOARD
────────────────────────────
D2 (RX)    →    TX
D3 (TX)    →    RX
5V         →    VCC
GND        →    GND

VS1053           MICROSD
────────────────────────────
CS         →    CS
SCK        →    SCK
MOSI       →    MOSI
MISO       →    MISO
GND        →    GND
```

**Note:** VS1053 requires SPI interface - exact pins depend on your VS1053 module. Refer to your module's datasheet.

---

## Power Requirements

### Power Calculation

**Component Power Consumption:**
- Arduino Uno: ~50mA
- SG90 Servo (idle): ~5mA each
- SG90 Servo (moving): ~100-200mA each
- VS1053: ~30mA

**Peak Current:** 50 + 600 + 30 = **~680mA** (all servos moving)

**Recommendation:** Use **5V 2A power supply** for safe margin

### Power Distribution

```
EXTERNAL 5V 2A SUPPLY
        │
        ├─────────────→ Arduino 5V pin (or VIN)
        │
        └─────────────→ Servo VCC rail
                        ├─ Head Servo
                        ├─ Left Arm Servo
                        └─ Right Arm Servo
```

**⚠️ IMPORTANT:** Don't power all 3 servos directly from Arduino's 5V pin when they're under load. Use external power supply.

---

## Step-by-Step Wiring Guide

### 1. Gather Components
- Arduino Uno R3
- 3x SG90 servos with headers
- VS1053 module
- MicroSD card (formatted FAT32)
- Breadboard or PCB
- Jumper wires (M-M, M-F)
- External 5V power supply (recommended)

### 2. Servo Connections

**Head Servo (Pin 9):**
1. Orange/White wire → Arduino D9
2. Red wire → 5V rail
3. Brown/Black wire → GND rail

**Left Arm Servo (Pin 10):**
1. Orange/White wire → Arduino D10
2. Red wire → 5V rail
3. Brown/Black wire → GND rail

**Right Arm Servo (Pin 8):**
1. Orange/White wire → Arduino D8
2. Red wire → 5V rail
3. Brown/Black wire → GND rail

### 3. VS1053 Connections

**Basic Setup:**
1. VS1053 TX → Arduino D2 (RX)
2. VS1053 RX → Arduino D3 (TX)
3. VS1053 VCC → 5V
4. VS1053 GND → GND

**MicroSD Card:**
1. Format SD card as FAT32
2. Create file named `rufus_tts.mp3`
3. Insert into VS1053 module

### 4. Power Connections

1. Connect external 5V supply positive (+) → Arduino 5V pin or VIN
2. Connect external supply negative (-) → Arduino GND
3. Connect common ground between Arduino and all components

### 5. Testing

**Test Arduino Connection:**
```bash
ls /dev/cu.usbserial*
# Should see your Arduino
```

**Test Servos:**
Upload test sketch to verify each servo moves correctly:

```cpp
#include <Servo.h>
Servo testServo;
void setup() {
  testServo.attach(9);
  testServo.write(90);
}
void loop() {
  testServo.write(40);
  delay(1000);
  testServo.write(120);
  delay(1000);
}
```

---

## Serial Communication

### Connection Settings
- **Baud Rate:** 9600
- **Data Bits:** 8
- **Parity:** None
- **Stop Bits:** 1

### Python → Arduino Commands

Send commands via serial (automatically handled by `arduino_controller.py`):

```python
import serial
arduino = serial.Serial('/dev/cu.usbserial-14210', 9600)
arduino.write(b'yes\n')  # Send "yes" gesture command
```

---

## Troubleshooting Wiring Issues

### Servo Not Moving
1. Check signal wire connection to correct PWM pin
2. Verify 5V power supply is connected
3. Check for loose ground connections
4. Test with simple servo sweep sketch

### Jittery Servos
1. Use external power supply (not Arduino 5V)
2. Add 100µF capacitor across servo power leads
3. Check for long wire runs (keep short)
4. Ensure good common ground

### VS1053 Not Playing
1. Verify MicroSD card is FAT32 formatted
2. Check file named exactly `rufus_tts.mp3`
3. Confirm SPI pin connections
4. Test VS1053 with example code from library

### Arduino Not Detected
```bash
# Mac
ls /dev/cu.usbserial*
ls /dev/cu.usbmodem*

# Linux
ls /dev/ttyUSB*
ls /dev/ttyACM*

# Windows
# Check Device Manager → Ports (COM & LPT)
```

---

## Shopping List

| Component | Quantity | Approx. Cost |
|-----------|----------|--------------|
| Arduino Uno R3 | 1 | $20 |
| SG90 Servo Motor | 3 | $5 each |
| VS1053 MP3 Module | 1 | $10 |
| MicroSD Card 4GB | 1 | $5 |
| INMP441 Microphone | 1 | $3 |
| 5V 2A Power Supply | 1 | $8 |
| Jumper Wires | Set | $5 |
| Breadboard | 1 | $5 |
| Cardboard | - | $0 (recycled) |

**Total:** ~$73 USD

---

## Next Steps

After wiring is complete:
1. Upload `arduino/rufus.ino` to Arduino
2. Test serial communication from Python
3. Run `python main.py` to start Rufus!
4. See [ASSEMBLY.md](ASSEMBLY.md) for cardboard shell construction

---

## Safety Notes

- Always disconnect power before wiring
- Double-check polarity (VCC/GND) before powering
- Don't power servos from Arduino 5V when under load
- Use appropriate current rating for power supply
- Keep wiring organized to avoid shorts
- Test each component individually before full assembly

---

## Reference Links

- [Arduino Servo Library](https://www.arduino.cc/reference/en/libraries/servo/)
- [VS1053 Datasheet](https://www.vlsi.fi/fileadmin/datasheets/vs1053.pdf)
- [SG90 Servo Specifications](https://www.servodatabase.com/servo/sg90)
- [Arduino Serial Communication](https://www.arduino.cc/reference/en/language/functions/communication/serial/)
