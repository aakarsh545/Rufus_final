# Rufus Robot - Assembly Instructions

Step-by-step guide to build Rufus's cardboard shell and assemble the robot.

## Overview

**Rufus Dimensions:**
- Total Height: 24cm
- Head: 9cm × 9.5cm × 5cm
- Torso: 15cm × 14.5cm × 10cm
- Arms: 9.5cm × 2.5cm × 3cm each

**Shell Design:**
- 3-shelf internal structure
- Open-back design for wiring access
- Front windows for Arduino display and mic
- Cardboard construction (easy to modify)

---

## Materials Needed

### Construction
- Cardboard sheets (corrugated, 3mm thickness)
- Craft knife or X-Acto knife
- Ruler and measuring tape
- Pencil and marker
- Hot glue gun + glue sticks
- Masking tape (for holding during assembly)

### Tools
- Scissors
- Cutting mat
- Straight edge
- Compass (for circles)

### Hardware (already wired)
- Arduino Uno (mounted)
- 3x SG90 servos (mounted in place)
- VS1053 module
- Wires (routed through back)

---

## Step 1: Cut Cardboard Pieces

### Head Pieces

**Front Face** (9cm × 9.5cm):
```
┌─────────────────────┐
│                     │
│    ┌───────────┐    │
│    │           │    │
│    │  MIC HOLE │    │  ← 3cm diameter circle
│    │    3cm    │    │     centered vertically
│    │           │    │
│    └───────────┘    │
│                     │
└─────────────────────┘
```

**Back Face** (9cm × 9.5cm):
- Solid piece (no holes)
- Leave top 2cm open for wiring access

**Side Pieces** × 2 (9cm × 5cm):
- Rectangular side walls

**Top/Bottom** × 2 (9.5cm × 5cm):
- Top has small hole for head servo mounting

### Torso Pieces

**Front Face** (15cm × 14.5cm):
```
┌─────────────────────────┐
│                         │
│  ┌─────────────────┐    │
│  │                 │    │
│  │   ARDUINO       │    │  ← 11cm × 7cm window
│  │   WINDOW        │    │    (cut out)
│  │                 │    │
│  │   11×7cm        │    │
│  └─────────────────┘    │
│                         │
└─────────────────────────┘
```

**Back Face** (15cm × 14.5cm):
- Full opening (no back panel)
- Use flaps/brackets to hold shelves

**Side Pieces** × 2 (15cm × 10cm):
- Full height sides

**Shelf Brackets** (internal):
- 3 shelves at specified heights
- Cut notches for Arduino, ESP32, VS1053

### Arm Pieces

**Upper Arms** × 2 (9.5cm × 2.5cm):
- Rectangular tubes
- Open at both ends

**Lower Arms** × 2 (6cm × 2.5cm):
- Slightly shorter
- Attach to servo horns

---

## Step 2: Assembly Order

### Phase 1: Internal Frame

1. **Create Shelf Structure**
   ```
   ┌───────────────────┐
   │  SHELF 1 (Arduino)│  ← Top
   ├───────────────────┤
   │  SHELF 2 (ESP32)  │  ← Middle (future)
   ├───────────────────┤
   │  SHELF 3 (VS1053) │  ← Bottom
   └───────────────────┘
   ```

2. **Mount Arduino**
   - Position Arduino on top shelf
   - Cut hole for USB access (back)
   - Mark and drill mounting holes
   - Use M3 screws and nuts or hot glue

3. **Mount Servos**
   - **Head Servo:** Attach to top of head frame
   - **Arm Servos:** Mount inside torso, aligned with arm holes
   - Use cardboard brackets + hot glue for secure mounting

4. **Install VS1053**
   - Place on bottom shelf
   - Ensure SD card is accessible from back
   - Leave room for wiring

### Phase 2: Head Assembly

1. **Assemble Head Box**
   - Glue front, sides, top, bottom
   - Leave back open for wiring

2. **Mount Head Servo**
   - Attach servo to bottom of head
   - Servo horn points down (connects to neck)
   - Reinforce with cardboard brackets

3. **Create Neck Connection**
   - Cardboard tube (5cm tall)
   - Attaches head servo to torso top
   - Route head servo wires through neck

### Phase 3: Torso Assembly

1. **Build Main Body**
   - Glue front face with Arduino window
   - Attach side panels
   - Create internal shelves
   - Leave back completely open

2. **Install Shelves**
   - Top shelf: Arduino Uno (11×7cm area)
   - Middle shelf: ESP32 Nano (4.5×1.8cm area)
   - Bottom shelf: VS1053 + SD card (3×3cm area)

3. **Mount Arm Servos**
   - Left arm servo: Inside left wall, 3cm from top
   - Right arm servo: Inside right wall, 3cm from top
   - Servo horns point outward through arm holes

### Phase 4: Arm Assembly

1. **Create Arm Linkages**
   - Attach servo horns to cardboard arm pieces
   - Use hot glue + reinforcement
   - Ensure smooth movement range

2. **Arm Movement Ranges**
   - Left arm: 0° (down) to 80° (up)
   - Right arm: 90° (down) to 180° (up)
   - Test before gluing permanently

### Phase 5: Final Assembly

1. **Connect Head to Torso**
   - Neck tube connects head servo to torso
   - Route head servo wires back to Arduino
   - Secure with hot glue

2. **Attach Arms**
   - Connect arm servos to arm pieces
   - Test movement range
   - Adjust servo limits in code if needed

3. **Wire Management**
   - Route all wires through back opening
   - Use twist ties or zip ties
   - Keep wires away from servo moving parts

4. **Close Up**
   - Verify all connections
   - Test all servos before sealing
   - Leave back open for easy access

---

## Step 3: Mounting Hardware

### Arduino Mounting Template

```
Arduino Uno Mounting Holes:
┌───────────────────────────┐
│ ● (14mm)          ● (14mm)│  ← Mounting holes
│                           │
│     [ARDUINO UNO]         │
│                           │
│ ● (14mm)          ● (14mm)│
└───────────────────────────┘
```

Use M3 screws (2.5mm) with nuts:
- Screw length: 15mm
- Spacer: 5mm (prevents crushing cardboard)

### Servo Mounting Brackets

Create cardboard brackets:

```
┌────────┐
│  ╱╲    │  ← L-bracket shape
│ ╱  ╲   │     Reinforce with
│╱____╲ │     extra layers
└────────┘
```

Glue 2-3 layers for strength.

---

## Step 4: Wiring Access & Management

### Back Opening

The entire back of the torso is open for easy access:

```
    ┌─────────────────────┐
    │   FRONT FACE        │
    │  (with window)      │
    ├─────────────────────┤
    │  [ARDUINO] ← VIEW   │
    ├─────────────────────┤
    │   OPEN BACK         │  ← No panel!
    │                     │     Easy wire access
    │                     │
    └─────────────────────┘
```

### Cable Routing

1. **Servo Wires**
   - Route through back opening
   - Keep slack for arm movement
   - Bundle with twist ties

2. **Power Wires**
   - External power enters from bottom back
   - Distribute to Arduino and servos

3. **USB Cable**
   - Arduino USB accessible from back
   - Use right-angle adapter if needed

---

## Step 5: Aesthetics & Finishing

### Optional Enhancements

1. **Paint/Decorate**
   - Acrylic paint works on cardboard
   - Add Rufus's face or design
   - Decorative elements

2. **Reinforcement**
   - Add packing tape on stress points
   - Extra cardboard layers on joints
   - Clear coat for durability

3. **LED Eyes** (future)
   - 2x LEDs in head for eyes
   - Connect to Arduino PWM pins
   - Add expressions!

4. **Face Plate**
   - Draw or print Rufus's face
   - Attach to head front
   - Make removable for upgrades

---

## Assembly Tips

### Hot Glue Tips
- Use low-temp glue gun (less cardboard warping)
- Apply glue to both surfaces for stronger bond
- Hold pieces in place until glue sets (~10 seconds)
- Reinforce joints with extra cardboard strips

### Cutting Cardboard
- Use sharp blade for clean cuts
- Cut on cutting mat to protect surface
- Score first, then cut through
- Use metal straight edge as guide

### Testing Before Final Assembly
1. Test all servos individually
2. Verify Arduino communication
3. Check VS1053 playback
4. Test arm movement ranges
5. Then glue everything permanently

---

## Troubleshooting Assembly

### Servo Hits Cardboard
1. Trim cardboard around servo
2. Adjust mounting position
3. Limit servo range in code

### Head Too Heavy
1. Use lighter cardboard material
2. Reinforce neck bracket
3. Adjust head servo center of gravity

### Arms Won't Move Full Range
1. Check arm hole position
2. Verify servo mounting angle
3. Adjust servo range in `config.py`

### Wiring Keeps Disconnecting
1. Add more slack to wires
2. Use strain relief (zip ties)
3. Route wires away from moving parts

---

## Assembly Checklist

**Head:**
- [ ] Front face with mic hole
- [ ] Back and side pieces
- [ ] Head servo mounted
- [ ] Neck connection built
- [ ] Wiring routed through neck

**Torso:**
- [ ] Front face with Arduino window
- [ ] Side panels assembled
- [ ] 3 internal shelves installed
- [ ] Arduino mounted
- [ ] VS1053 mounted
- [ ] Back left open for access

**Arms:**
- [ ] Arm pieces cut and assembled
- [ ] Arm servos mounted
- [ ] Servo horns connected to arms
- [ ] Movement tested

**Final:**
- [ ] Head attached to torso
- [ ] Arms connected and moving
- [ ] All wires connected
- [ ] Power supply tested
- [ ] Arduino communication verified

---

## Next Steps

After assembly is complete:
1. Upload firmware: `arduino/rufus.ino`
2. Install Python dependencies: `pip install -r requirements.txt`
3. Configure: Set `OPENAI_API_KEY` environment variable
4. Run Rufus: `python main.py`

Enjoy your new AI robot companion! 🤖

---

## Reference: Shell Dimensions

```
        ┌─────────┐ 9cm
       ╱           ╲
      │  HEAD      │ 9.5cm
       ╲           ╱
        └─────────┘ 5cm
           │ 3cm    ← Neck
    ┌─────────────┐
    │             │
    │  TORSO      │ 15cm
    │  (Arduino)  │ 14.5cm
    │             │ 10cm
    └─────────────┘
      │         │
     ARM       ARM
```

**Total Height:** 24cm
**Width:** 14.5cm
**Depth:** 10cm

Perfect size for a desk companion! 🤖
