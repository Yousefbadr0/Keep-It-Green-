/*
  Keep It Green — Arduino Compartment Controller  (Arduino NANO + 2× SG90)
  ========================================================================
  Receives one-byte commands from the laptop (machine.py) over USB serial and
  opens the matching compartment with an SG90 micro-servo:

      'P' -> Plastic compartment   (Servo 1, pin D9)
      'A' -> Aluminum compartment  (Servo 2, pin D10)
      'O' -> Rejected item         (red LED blink, no compartment)   [optional]
      'T' -> Self-test both gates  (use the serial tester to verify wiring)

  ---------------------------------------------------------------------------
  WIRING  (Arduino Nano)                     SG90 servo leads
  ---------------------------------------------------------------------------
    Plastic servo  signal (orange) -> D9        orange/yellow = SIGNAL
    Aluminum servo signal (orange) -> D10       red           = +5V
    Green LED (+ 220R) ------------ -> D7        brown/black   = GND
    Red   LED (+ 220R) ------------ -> D6
    Both servos  +5V (red) -------- -> 5V *          * SEE POWER NOTE
    Both servos  GND (brown) ------ -> GND
    LED cathodes ------------------ -> GND

  POWER NOTE (important for 2× SG90):
    One SG90 can draw ~100-250 mA, and >400 mA at stall. Two of them may exceed
    what the Nano's onboard 5V/USB can supply, causing brown-outs / random resets.
    For reliable operation power the servos from a SEPARATE 5V supply (e.g. a
    5V 2A adapter or a UBEC) and join the grounds:  servo +5V -> external 5V,
    servo GND -> external GND AND Nano GND (COMMON GROUND is required).
    For a quick bench test one servo at a time off the Nano 5V is usually fine.

  Design notes:
    - NON-BLOCKING: a millis() state machine runs the open/close cycle so the
      board keeps reading serial and never misses a command (no delay() stalls).
    - Servos DETACH after closing to stop holding-torque jitter/buzzing/heat.
    - On boot it runs a SELF-TEST (both gates open+close) so you can confirm the
      wiring works with NO laptop connected.  Set BOOT_SELFTEST=false to skip.
    - Sends ACKs back to the laptop: "READY", "ACK:P", "DONE:P", "REJECT".
    - Baud 9600 — must match machine.py BAUD_RATE.
*/

#include <Servo.h>

// ─── Pin config  (change here if you wire to different pins) ──────────────────
const int SERVO_PLASTIC_PIN  = 9;
const int SERVO_ALUMINUM_PIN = 10;
const int LED_GREEN_PIN      = 7;   // lights while a compartment is open (optional)
const int LED_RED_PIN        = 6;   // blinks on a rejected item          (optional)

// ─── Servo angles / timing  (tune for your gate mechanism) ───────────────────
const int           CLOSE_ANGLE = 0;      // gate shut
const int           OPEN_ANGLE  = 90;     // gate open (SG90 range is 0..180)
const unsigned long OPEN_MS     = 3000;   // how long the compartment stays open
const unsigned long REJECT_MS   = 500;    // red LED blink duration
const bool          BOOT_SELFTEST = true; // sweep both gates once on power-up

Servo servoPlastic;
Servo servoAluminum;

// ─── Non-blocking state machine ───────────────────────────────────────────────
enum State { IDLE, OPENING, REJECTING };
State         state       = IDLE;
unsigned long stateStart  = 0;
Servo*        activeServo = nullptr;
char          activeCmd   = 0;


// Blocking open+close of one gate — used only by the self-test / 'T' command.
void testGate(Servo &servo, int pin, const char *name) {
  Serial.print("TEST:"); Serial.println(name);
  servo.attach(pin);
  servo.write(OPEN_ANGLE);  delay(700);
  servo.write(CLOSE_ANGLE); delay(700);
  servo.detach();
}

void selfTest() {
  digitalWrite(LED_GREEN_PIN, HIGH);
  testGate(servoPlastic,  SERVO_PLASTIC_PIN,  "PLASTIC");
  testGate(servoAluminum, SERVO_ALUMINUM_PIN, "ALUMINUM");
  digitalWrite(LED_GREEN_PIN, LOW);
  Serial.println("SELFTEST:DONE");
}


void setup() {
  Serial.begin(9600);
  pinMode(LED_GREEN_PIN, OUTPUT);
  pinMode(LED_RED_PIN,   OUTPUT);

  // Set both gates to the closed position, then detach to stop jitter.
  servoPlastic.attach(SERVO_PLASTIC_PIN);
  servoAluminum.attach(SERVO_ALUMINUM_PIN);
  servoPlastic.write(CLOSE_ANGLE);
  servoAluminum.write(CLOSE_ANGLE);
  delay(500);
  servoPlastic.detach();
  servoAluminum.detach();

  if (BOOT_SELFTEST) selfTest();   // move both gates so you can verify wiring
  Serial.println("READY");
}


// Begin opening a compartment (returns immediately — non-blocking).
void beginOpen(Servo &servo, int pin, char cmd) {
  activeServo = &servo;
  activeCmd   = cmd;
  servo.attach(pin);
  servo.write(OPEN_ANGLE);
  digitalWrite(LED_GREEN_PIN, HIGH);
  state      = OPENING;
  stateStart = millis();
  Serial.print("ACK:"); Serial.println(cmd);
}

void beginReject() {
  digitalWrite(LED_RED_PIN, HIGH);
  state      = REJECTING;
  stateStart = millis();
  Serial.println("REJECT");
}

void handleSerial() {
  if (Serial.available() <= 0) return;
  char cmd = (char)Serial.read();

  if (cmd == 'T') { selfTest(); return; }   // manual test (allowed any time)
  if (state != IDLE) return;                // ignore P/A/O mid-cycle

  if      (cmd == 'P') beginOpen(servoPlastic,  SERVO_PLASTIC_PIN,  'P');
  else if (cmd == 'A') beginOpen(servoAluminum, SERVO_ALUMINUM_PIN, 'A');
  else if (cmd == 'O') beginReject();
}

void updateState() {
  unsigned long now = millis();
  if (state == OPENING && now - stateStart >= OPEN_MS) {
    activeServo->write(CLOSE_ANGLE);
    delay(300);                 // brief settle before detaching
    activeServo->detach();      // stop holding torque -> no jitter
    digitalWrite(LED_GREEN_PIN, LOW);
    Serial.print("DONE:"); Serial.println(activeCmd);
    state = IDLE;
    activeServo = nullptr;
  }
  else if (state == REJECTING && now - stateStart >= REJECT_MS) {
    digitalWrite(LED_RED_PIN, LOW);
    state = IDLE;
  }
}

void loop() {
  handleSerial();   // read commands (never blocked)
  updateState();    // advance the open/close cycle
}
