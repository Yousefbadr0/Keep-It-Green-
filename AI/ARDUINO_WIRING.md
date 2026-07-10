# Keep It Green — Arduino Wiring & Test Guide

Hardware you are using: **Arduino Nano** + **2× SG90 micro-servos** (plastic gate + aluminium gate).

---

## 1. Wiring

Each SG90 has 3 wires: **orange/yellow = signal**, **red = +5 V**, **brown/black = GND**.

| From (Arduino Nano) | To | Notes |
|---|---|---|
| **D9** | Plastic servo **signal** (orange) | PWM pin |
| **D10** | Aluminium servo **signal** (orange) | PWM pin |
| **5V** | Both servos **+5V** (red) | ⚠️ see Power note |
| **GND** | Both servos **GND** (brown) | must be common ground |
| **D7** → 220 Ω → LED → GND | Green LED (optional) | on while a gate is open |
| **D6** → 220 Ω → LED → GND | Red LED (optional) | blinks on a rejected item |

```
   Arduino Nano                       SG90 (plastic)
   ┌──────────┐        orange  ┌──────────────┐
   │       D9 ├────────────────┤ signal        │
   │       D10├──────┐         │ +5V ─── red   │
   │       5V ├──────┼────┬────┤ GND ─── brown │
   │      GND ├──────┼────┼─┐  └──────────────┘
   │       D7 ├─[220Ω]─▶│ │ │      SG90 (aluminium)
   │       D6 ├─[220Ω]─▶│ │ │  ┌──────────────┐
   └──────────┘   green red│ └──┤ signal (D10)  │
                    LEDs    └────┤ +5V / GND     │
                                 └──────────────┘
```

### ⚠️ Power note (read this)
One SG90 draws ~100–250 mA, and **>400 mA at stall**. Two of them can exceed what the
Nano's USB/5V pin can supply and cause **brown-outs / random resets**.

- **Bench test (one servo, short moves):** powering from the Nano **5V** pin is usually fine.
- **Real machine (both servos):** power the servos from a **separate 5 V supply** (5 V/2 A
  adapter or a UBEC). **Join the grounds** — servo GND must connect to **both** the external
  supply GND **and** the Nano GND (common ground). Signal wires still go to D9/D10.

---

## 2. Flash the sketch

1. Open **`recycling_machine.ino`** in the Arduino IDE. (If the IDE asks to move it into a
   folder named `recycling_machine`, say yes.)
2. **Tools → Board → Arduino Nano.**
3. **Tools → Processor →** `ATmega328P` — if upload fails, try **`ATmega328P (Old Bootloader)`**
   (most clone Nanos need this).
4. **Tools → Port →** your Nano's port (e.g. `COM5`). If no port appears, install the
   **CH340** USB driver (most clone Nanos) or the FTDI driver.
5. Click **Upload**.

On power-up the sketch runs a **self-test**: both gates open and close once. If they move,
your wiring is correct — you can verify this **with no laptop program running**.

---

## 3. Test it (before the full machine)

Use the bench tester — it talks to the Arduino directly, no camera/model needed:

```bash
pip install pyserial
python arduino_test.py --list     # find your port, e.g. COM5
python arduino_test.py COM5       # open it
```

Then type:
- `P` → plastic gate opens ~3 s and closes
- `A` → aluminium gate opens and closes
- `T` → self-test both gates
- `auto` → fires P, A, P, A automatically
- `q` → quit

You should see replies like `READY`, `ACK:P`, `DONE:P`.

---

## 4. Connect it to the real machine

When the bench test works, plug the Nano into the machine laptop and tell `machine.py`
which port to use. In **`machine.py`** (top of the file) change **one line**:

```python
ARDUINO_PORT = None        # <-- change to your port, e.g. "COM5"  (Linux: "/dev/ttyUSB0")
```

That's the only change needed — `machine.py` already sends `P`/`A` on each accepted item,
which matches the sketch. Baud is 9600 on both sides.

- Leave `ARDUINO_PORT = None` and the machine runs fine **without** the Arduino (no sorting).
- Set it to your port and the servos actuate on every accepted item.
- Tip: run `machine.py` — even in **SIMULATE mode** (no camera/model) it auto-generates items,
  so you can watch the servos fire end-to-end.

---

## 5. Things you may want to adjust (all at the top of `recycling_machine.ino`)

| Setting | Default | Change if… |
|---|---|---|
| `SERVO_PLASTIC_PIN` / `SERVO_ALUMINUM_PIN` | 9 / 10 | you wired the signal to different pins |
| `OPEN_ANGLE` / `CLOSE_ANGLE` | 90 / 0 | the gate opens the wrong way or not far enough |
| `OPEN_MS` | 3000 ms | the item needs more/less time to drop through |
| `BOOT_SELFTEST` | true | set `false` once installed, to skip the power-up sweep |
| `LED_GREEN_PIN` / `LED_RED_PIN` | 7 / 6 | you don't use the LEDs, or wired them elsewhere |

**Serial commands the board understands:** `P` (plastic), `A` (aluminium), `O` (reject blink),
`T` (self-test). Replies: `READY`, `ACK:x`, `DONE:x`, `REJECT`, `TEST:…`, `SELFTEST:DONE`.
