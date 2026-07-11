"""
Keep It Green — Arduino bench tester
====================================
Drives the sorter Arduino DIRECTLY over serial, so you can verify the servos
and wiring BEFORE plugging into the full machine (no camera / model needed).

Usage:
    pip install pyserial
    python arduino_test.py --list          # list available COM ports
    python arduino_test.py COM5            # open that port and go interactive
    python arduino_test.py                 # uses PORT below

Then type a command and press Enter:
    P  -> open the PLASTIC gate
    A  -> open the ALUMINUM gate
    O  -> reject blink (red LED)
    T  -> self-test BOTH gates
    auto -> fire P, A, P, A automatically
    q  -> quit
Replies from the board (READY / ACK / DONE / TEST ...) are printed with '<-'.
"""

import sys
import time
import threading

try:
    import serial
    from serial.tools import list_ports
except ImportError:
    print("pyserial is not installed.  Run:  pip install pyserial")
    sys.exit(1)

# ─── change this to your Arduino Nano port (or pass it on the command line) ───
PORT = "COM5"          # Windows: COM3/COM5...   Linux: /dev/ttyUSB0   Mac: /dev/cu.usbserial-*
BAUD = 9600            # must match the sketch's Serial.begin() and machine.py BAUD_RATE


def list_available():
    ports = list(list_ports.comports())
    if not ports:
        print("No serial ports found. Is the Nano plugged in and the CH340/FTDI driver installed?")
        return
    print("Available serial ports:")
    for p in ports:
        print(f"  {p.device:12} {p.description}")


def reader(ser):
    while True:
        try:
            line = ser.readline().decode(errors="ignore").strip()
        except Exception:
            break
        if line:
            print("  <-", line)


def main():
    args = sys.argv[1:]
    if "--list" in args or "-l" in args:
        list_available()
        return

    port = next((a for a in args if not a.startswith("-")), None)
    ser = None
    # If no port was given, or the given one fails, AUTO-DETECT (Windows renumbers
    # COM ports on replug — this is the usual reason a fixed port "does nothing").
    candidates = [port] if port else []
    if not candidates:
        found = list(list_ports.comports())
        found.sort(key=lambda p: any(k in f"{p.description} {p.hwid}".lower()
                   for k in ("arduino", "ch340", "usb-serial", "wch", "cp210", "ftdi", "silabs")), reverse=True)
        candidates = [p.device for p in found]
        if candidates:
            print("Auto-detecting Arduino among:", ", ".join(candidates))
    for p in candidates:
        print(f"Opening {p} @ {BAUD} baud ...")
        try:
            ser = serial.Serial(p, BAUD, timeout=1)
            port = p
            break
        except Exception as e:
            print(f"  could not open {p}: {e}")
    if ser is None:
        print("[ERROR] no Arduino could be opened.")
        list_available()
        print("Tip: close the Arduino IDE Serial Monitor (it locks the port) and check the cable.")
        return
    print(f"Connected on {port}.  (Ctrl-C to quit)")

    time.sleep(2.0)  # the Nano reboots when the port opens — wait for it
    threading.Thread(target=reader, args=(ser,), daemon=True).start()

    print("Commands:  P  A  O  T  auto  q")
    try:
        while True:
            cmd = input("cmd> ").strip()
            if cmd.lower() in ("q", "quit", "exit"):
                break
            if cmd.lower() == "auto":
                for c in ("P", "A", "P", "A"):
                    print(f"  -> {c}")
                    ser.write(c.encode())
                    time.sleep(4.0)   # let each gate open + close
                continue
            if cmd:
                ser.write(cmd[0].upper().encode())
    except KeyboardInterrupt:
        pass
    finally:
        ser.close()
        print("\nClosed.")


if __name__ == "__main__":
    main()
