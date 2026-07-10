# Handoff: Keep It Green — Brand & Surfaces

## Overview
**Keep It Green** is a smart-recycling reward system: users scan a recycling machine, drop bottles/cans, an on-device YOLO model classifies the item, the correct compartment opens, and the user earns points redeemable for vendor promo codes. This package contains the **brand identity** and the **recommended tech stack** for each surface (mobile app, machine kiosk, website, backend), ready to hand to Claude Code.

## About the design files
The HTML file in this bundle (`Keep It Green Brand.dc.html`) is a **design reference** — a high-fidelity prototype of the brand system, not production code to ship. The task is to **rebuild these designs in each target environment** (Flutter, a web kiosk, Next.js) using that environment's idiomatic patterns, pulling exact values from the tokens in `/brand`.

## Fidelity
**High-fidelity.** Colors, typography, radii, and motion are final. Match them exactly.

---

## Screens / Views
The full screen-by-screen designs are in the HTML references (open in a browser):
- **`Keep It Green App.dc.html`** — 7 mobile screens: 01 Welcome/Auth · 02 Home · 03 Scan QR · 04 Live session · 05 Rewards · 06 Redeemed · 07 History.
- **`Keep It Green Machine.dc.html`** — 5 kiosk states: 01 Idle/Welcome · 02 Session active (place item) · 03 Item detected · 04 Drop it in (compartment opens) · 05 Session summary.

## Brand system (recreate exactly)

### Logo
The mark is a **single leaf inside a rounded "token"** — the same shape points live in, so the mark reads as *recycling = reward*. Leaf veins double as motion lines.
- `assets/logo-app-icon.svg` — green token + white leaf (app icon / favicon)
- `assets/app-icon-1024.png`, `-512.png`, `-192.png` — rasterized icons (iOS / Android / web)
- `assets/logo-leaf-green.svg` — leaf only, for light backgrounds
- `assets/logo-leaf-white.svg` — leaf only, for dark backgrounds
- `assets/logo-lockup-horizontal.svg` — mark + "Keep It **Green**" wordmark (needs Space Grotesk to render text; outline or recreate in code for production)
- **Monogram:** `KIG` set in Space Grotesk Bold
- **Clear space:** ≥ 0.5× the token height on all sides. **Min size:** 32px.

### Color  (also in `brand/tokens.css` / `tokens.json`)
- Spring Green `#18C964` — primary: mark, CTAs, accents
- Deep Forest `#0C3B2A` — dark surfaces: hero, machine panels
- Sun `#FFC83D` — reward accent: points, badges, coins
- Mint `#DCF1E2` — tint surface
- Paper `#F6F7F1` — app / page background
- Charcoal `#13201A` — text · Muted `#6B7A72` — secondary text

### Typography
- **Space Grotesk** (400/500/700) — headings, numbers, UI labels. Labels are uppercase, letter-spacing `.14em`.
- **Hanken Grotesk** (400/500/600/700) — body copy, line-height ~1.7.
- Scale (px): Display 52 · H1 32 · Subtitle 22 · Body 17 · Label 13.

### Motion
Springy and rewarding. Actions land with a small overshoot (`cubic-bezier(.2,.8,.3,1.4)`); **points always count up**; the leaf gently grows. Never stiff, never slow. Keep durations ~0.6–0.9s.

---

## Recommended stack (per surface)

These align with the team's existing plan (3 AI, 2 .NET, 1 Flutter).

### 1. Mobile app — **Flutter**
- Flutter + Material 3 (`useMaterial3: true`), theme in `brand/flutter_theme.dart`
- `google_fonts` (Space Grotesk + Hanken Grotesk)
- State: **Riverpod** (`flutter_riverpod`)
- Routing: `go_router`
- Networking: `dio` → the .NET API
- QR scanning: `mobile_scanner`
- JWT storage: `flutter_secure_storage`
- Core screens: Onboarding/Auth → Home (points balance) → **Scan QR** → Live session (detected item + points count-up) → Rewards catalog → Redeem → History.

### 2. Machine kiosk — **Python web kiosk** (reuses these HTML designs almost 1:1)
- The laptop already runs Python for YOLO, so serve the UI from the same process:
  - **FastAPI** serving a fullscreen HTML/CSS/JS page; **WebSocket** pushes live events (detected type, confidence, points, door state) to the screen.
  - Run **Chromium in `--kiosk`** fullscreen on the laptop.
- AI: **Ultralytics YOLO (v8/11)** + **OpenCV** capture; classes: Plastic Bottle / Aluminum Can / Other.
- Hardware: **pyserial** → Arduino. Protocol: send `P` (plastic), `A` (aluminum), `O` (other). Arduino C++ sketch reads serial and drives the matching servo.
- *Alternative:* Flutter **desktop** (shares code with the app) if you'd rather not run a browser.

### 3. Website — **Next.js (App Router) + Tailwind**
- Marketing/landing + a **vendor portal** (manage promo codes, view redemptions).
- Map `tokens.json` into `tailwind.config` (`spring`, `forest`, `sun`, …); load both fonts via `next/font/google`.

### 4. Backend — **ASP.NET Core Web API** (already chosen)
- .NET 8 Web API + **EF Core** + **SQL Server**, **JWT** auth (`Microsoft.AspNetCore.Authentication.JwtBearer`).
- Images: store files in blob/local storage, **only the path in DB** (as planned).
- Add **SignalR** for real-time machine ↔ backend session/transaction events.
- Tables per the project spec: Users, Machines, Sessions, Transactions, Vendors, PromoCodes, Redemptions.

---

## How to hand this to Claude Code
1. **Download this folder** (zip) and unzip it into — or beside — your repo.
2. Open the repo in Claude Code.
3. Copy a prompt from **`CLAUDE_CODE_PROMPT.md`** (one each for app / kiosk / website), paste it into Claude Code, and point it at this folder. Each prompt tells it to read `/brand/tokens.*` and the brand board for exact values.
4. Build one surface at a time. Start with the **mobile app** or **machine kiosk** — they're the demo-critical surfaces for a grad project.

## Files in this bundle
- `Keep It Green Brand.dc.html` — the brand board prototype (open in a browser)
- `Keep It Green App.dc.html` — 7 mobile app screens (Welcome, Home, Scan, Live session, Rewards, Redeemed, History)
- `Keep It Green Machine.dc.html` — 5 machine kiosk states (Idle, Waiting, Detected, Drop-it-in, Summary)
- `assets/` — logo SVGs + PNG app icons + favicon
- `brand/tokens.css`, `brand/tokens.json` — design tokens (source of truth)
- `brand/flutter_theme.dart` — ready-made Flutter ThemeData
- `CLAUDE_CODE_PROMPT.md` — copy-paste prompts for Claude Code
