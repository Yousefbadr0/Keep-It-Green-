# Keep It Green 🌱

An AI-powered smart recycling reward system — graduation project, Menoufia University,
Faculty of Electronic Engineering, Dept. of Computer Science & Engineering (2024–2025).

A user pairs their phone with a recycling machine (ATM-style QR / 6-digit code), inserts
plastic bottles or aluminium cans, a YOLOv8 detector recognizes the material, an Arduino
opens the right compartment, and reward points land on the user's account instantly.

**Live demo:** https://keepitgreen.runasp.net (web app + kiosk + Swagger API docs)

## Repository map

| Folder | What it is | Tech |
|---|---|---|
| `Recycle/` | Backend REST API + web app + kiosk UI (served from `wwwroot/`) | ASP.NET Core (.NET 10), EF Core, SQL Server, JWT |
| `Mobile/` | User + admin mobile app | Flutter (Dart), Material 3 |
| `AI/` | The machine: detector + kiosk driver + Arduino | Python, Ultralytics YOLOv8, pywebview, pyserial |
| `AI/recycling_machine/` | Arduino Nano sketch (2× SG90 servo sorter) | Arduino C++ |
| `Database/` | DDL, backup, ER diagrams, SRS | SQL Server |
| `tests/` | End-to-end API test suites (run against local or live) | Python + requests |
| `Book/` | 105-page graduation book (docx + pdf + assets) | — |
| `Presentation/` | Defense deck + technical deck + scripts | — |
| `Design/`, `Prototype_Boxes/`, `design_handoff_keep_it_green/` | 3D model, renders, brand assets | Blender |
| `Dataset` (archived) | Training data lives on Kaggle; see `AI/keep-it-green_V4.ipynb` | — |
| `_archive/` | Old versions, build scripts, superseded artifacts (safe to delete) | — |

## Architecture (one paragraph)

Five components, one rule: **no client ever touches the database** — everything goes
through the authenticated API. The machine authenticates with an `X-Machine-Key` header;
humans authenticate with JWT (role-based: User / Admin). The machine starts a session →
backend issues a unique pairing code → phone pairs → every accepted item posts a
transaction credited to exactly that user → finishing on either side (phone button or
machine timeout) ends the session on both.

## Running each part

### Backend (serves API + web + kiosk)
```bash
cd Recycle
dotnet run          # http://localhost:5217 — migrations + admin seed run automatically
```
Secrets (connection string, JWT key, machine key, admin seed) come from
`appsettings.json` locally and from the deployed config in production — the committed
file contains **dev values only**. See `DEPLOYMENT.md` for the MonsterASP publish/zip flow.

### Mobile app
```bash
cd Mobile
flutter pub get
flutter run                    # or: flutter build apk --release
```
Points at the live backend by default; override in-app via the Server settings screen.

### Machine (detector + kiosk)
```bash
cd AI
pip install pywebview ultralytics opencv-python pyserial requests "qrcode[pil]"
python machine.py
```
Configuration lives in `AI/machine_config.json` (not committed — copy the example below)
or environment variables `KIG_BACKEND`, `KIG_MACHINE_KEY`, `KIG_MACHINE_ID`:
```json
{ "backend_base": "https://keepitgreen.runasp.net", "machine_key": "<key>",
  "machine_id": 2, "location": "Cairo", "arduino_port": "COM5" }
```
No camera/model installed → it runs in SIMULATE mode (auto-generates items for demos).
Isolated model check: `python test_webcam.py` (watch the `area=` column — ~100% on a
real item means the model failed to localize).

### Arduino sorter
Open `AI/recycling_machine/recycling_machine.ino` in Arduino IDE → Board: *Arduino Nano*
(clones: Processor = *ATmega328P (Old Bootloader)*, CH340 driver) → flash. It self-tests
both gates on power-up. Wiring + power notes: `AI/ARDUINO_WIRING.md`.
Serial protocol 9600 baud: `P` = plastic gate, `A` = aluminium gate, `T` = self-test.

### Tests (23 core + 12 admin + 13 concurrency checks)
```bash
cd tests
set KIG_BASE=https://keepitgreen.runasp.net   # or http://localhost:5217
set KIG_ADMIN_PW=<admin password>             # needed by admin/concurrency suites
python e2e_test.py && python admin_test.py && python concurrency_test.py
```

## The AI model (V4)

YOLOv8s (11.1M params), 2 classes (`plastic_bottle`, `aluminum_can`), trained on
**11,897 real-box images** fused from 4 public detection datasets (Drinking Waste,
Beverage Containers, YOLO Waste Detection, Can/Bottle/Pack) with verified per-dataset
class maps — **no synthetic/full-frame labels**. Held-out test: **mAP@0.5 = 0.928**
(plastic 0.870 / aluminium 0.986), ~69 FPS GPU. Non-recyclables are rejected by a 0.65
confidence gate (open-set rejection). Training notebook: `AI/keep-it-green_V4.ipynb`
(runs on Kaggle, dual T4). Weights: `AI/keep_it_green_best.pt`.

## Deployment

Live on MonsterASP.NET (free tier). Full recipe (publish → trim → forward-slash zip →
app_offline upload) in `DEPLOYMENT.md`.

## Team

Yousef Badr · Eslam Medhat · Ahmed Anwer · Mohanad Ayman · Menna Osama · Shahd El Aswad

## Known technical debt (deliberate, documented)

- ~68 nullable-reference warnings in the backend (no errors) — enable NRT cleanup pass later.
- No rate limiting on `/api/User/Login` — acceptable at pilot scale, add before real scale.
- CORS is open (`AllowAll`) — safe for a JWT-bearer API (no cookies), tighten if cookies ever appear.
- Release APK is debug-signed — create a proper keystore before any store submission.
