# Claude Code — copy-paste prompts

Unzip this folder into (or next to) your repo first. Each prompt assumes Claude Code can read
`brand/tokens.json`, `brand/tokens.css`, `brand/flutter_theme.dart`, and the design references:
`Keep It Green Brand.dc.html` (brand board), `Keep It Green App.dc.html` (7 mobile screens),
and `Keep It Green Machine.dc.html` (5 kiosk states). Open them in a browser to see the exact look.

---

## 0. Shared preface (paste at the top of any prompt)

> You are building **Keep It Green**, a smart-recycling rewards product. Before writing code, read
> `design_handoff_keep_it_green/brand/tokens.json` and open `Keep It Green Brand.dc.html` to absorb the
> brand: Spring Green `#18C964` (primary), Deep Forest `#0C3B2A` (dark surfaces), Sun `#FFC83D` (points/rewards),
> Paper `#F6F7F1`, Charcoal `#13201A`. Fonts: **Space Grotesk** (headings/numbers/labels) + **Hanken Grotesk** (body).
> Motion is springy and rewarding — overshoot on actions, points always count up. Match these exactly.

---

## 1. Mobile app (Flutter)

> [Shared preface]
>
> Scaffold a **Flutter** app (Material 3) using `design_handoff_keep_it_green/brand/flutter_theme.dart` as the theme.
> Add deps: `flutter_riverpod`, `go_router`, `dio`, `mobile_scanner`, `flutter_secure_storage`, `google_fonts`.
> **Match `Keep It Green App.dc.html` screen-for-screen** — it has all 7 designs (Welcome, Home, Scan, Live
> session, Rewards, Redeemed, History). Build them with the Keep It Green look:
> 1. **Welcome / Auth** (sign up / log in) — JWT stored in secure storage. Forest background, leaf token.
> 2. **Home** — points balance card (Forest card, Sun number), big "Scan a machine" button, nearby machines.
> 3. **Scan** — full-screen `mobile_scanner` with the green corner-bracket frame to read a machine QR.
> 4. **Live session** — shows each detected item (Plastic / Aluminum / Other) with a "+15 pts" badge and
>    **animates the total counting up** on accept; lists items dropped this session.
> 5. **Rewards** — vendor promo grid with points-cost pills; tap a reward to **Redeem** (deducts points).
> 6. **Redeemed** — success screen revealing the promo code in a dashed box, shows new balance.
> 7. **History** — transactions and redemptions grouped by Today / This week.
>
> Use a `dio` API client pointing to a configurable base URL for the .NET backend. Keep widgets reusable
> (PointsBadge, MachineCard, RewardTile). Use the leaf app icon from `assets/`.

---

## 2. Machine kiosk (Python + FastAPI + HTML)

> [Shared preface]
>
> Build the **recycling-machine kiosk UI** that runs on the laptop. Use **FastAPI** to serve a single
> fullscreen HTML/CSS/JS page and a **WebSocket** that the detection loop pushes events to. **Match
> `Keep It Green Machine.dc.html`** — it has all 5 states: **Idle/Welcome** ("Ready when you are" + QR) →
> **Session active** (waiting for item, green target frame) → **Detected** (item type + confidence + "+15
> points", springy reveal) → **Drop it in** (the correct compartment highlighted OPEN) → **Session summary**
> (items recycled + points earned, Spring Green screen).
>
> Wire it to the hardware pipeline:
> - YOLO inference with **Ultralytics** + **OpenCV** webcam capture; classes Plastic Bottle / Aluminum Can / Other.
> - On accept above a confidence threshold, POST the transaction to the .NET backend, then send a serial
>   command to Arduino via **pyserial**: `P` plastic, `A` aluminum, `O` other.
> - Push every state change to the kiosk page over WebSocket so the UI animates in real time.
> Also give me a minimal **Arduino C++ sketch** that reads the serial char and drives Servo 1 (plastic) or Servo 2 (aluminum).
> Launch instructions: run Chromium in `--kiosk` pointed at the local FastAPI URL.

---

## 3. Website (Next.js + Tailwind)

> [Shared preface]
>
> Build a **Next.js (App Router) + Tailwind** site. Map `brand/tokens.json` colors into `tailwind.config`
> (spring, forest, sun, mint, paper, charcoal) and load Space Grotesk + Hanken Grotesk via `next/font/google`.
> Deliver: (a) a **marketing landing page** (hero with the leaf lockup, how-it-works: scan → drop → earn → redeem,
> machine locations, app download CTAs) in the Keep It Green style; and (b) a **vendor portal** (auth, create/manage
> promo codes, view redemptions) that talks to the .NET API. Reuse the leaf SVGs from `assets/`.

---

## 4. Backend (ASP.NET Core) — optional, if not started

> Build an **ASP.NET Core (.NET 8) Web API** with **EF Core + SQL Server** and **JWT** auth. Entities:
> Users, Machines, Sessions, Transactions, Vendors, PromoCodes, Redemptions (see the project spec). Endpoints
> for auth, session start/stop, transaction logging (store image path only), rewards listing, and redemption.
> Add **SignalR** for real-time machine ↔ backend events. Provide EF migrations and seed data.
