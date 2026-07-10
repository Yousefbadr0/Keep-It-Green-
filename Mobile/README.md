# Keep It Green — Mobile App (Flutter)

The user-facing app, built to the **official design handoff** (`design_handoff_keep_it_green`):
Space Grotesk + Hanken Grotesk, Spring Green `#18C964` / Deep Forest `#0C3B2A` / Sun `#FFC83D`,
springy motion, points always count up. All times are shown in **Cairo time** (`Africa/Cairo`, DST-aware).

## The flow (matches `Keep It Green App.dc.html`)

```
Welcome → Home → "Scan a machine" → Scan QR (or enter code) → PAIR → Live session → Finish
                                   Rewards → Redeem → Redeemed (promo code)
                                   Activity (Today / Earlier, Cairo time)
```

The machine shows a **QR + 6-digit code** (the ATM kiosk). The user **scans it** here (or types it),
which calls `POST /api/Otp/Pair` to open the session — then recycles at the machine while the
**Live session** screen shows items + points counting up.

| Screen | File |
|---|---|
| 01 Welcome / Auth | `welcome_screen.dart`, `login_screen.dart`, `register_screen.dart` |
| 02 Home (points, scan, nearby) | `home_tab.dart` |
| 03 Scan QR (`mobile_scanner`) | `scan_screen.dart` |
| 04 Live session | `live_session_screen.dart` |
| 05 Rewards catalog | `rewards_tab.dart` |
| 06 Redeemed | `redeemed_screen.dart` |
| 07 Activity / History | `history_tab.dart` |
| Profile / logout | `profile_tab.dart` |

Shared: `theme.dart` (brand), `widgets.dart` (LeafToken, PointsPill), `cairo.dart` (Cairo time), `services/api_service.dart`.

## Setup & run

> Requires a recent **Flutter** (3.27+) with Dart 3.

1. **Generate platform folders** (repo ships only `lib/` + `pubspec.yaml`):
   ```bash
   cd "D:\Graduation Project\Mobile"
   flutter create .
   ```

2. **Camera permission for the QR scanner** — one command (patches the generated Android/iOS files):
   ```bash
   powershell -ExecutionPolicy Bypass -File setup_permissions.ps1
   ```
   This adds the Android `CAMERA` permission and the iOS `NSCameraUsageDescription`. It's
   idempotent (safe to re-run). `mobile_scanner` needs Android **minSdk 21+** — Flutter's
   default already satisfies this.

3. **Point at your backend** — `lib/services/api_service.dart`:
   ```dart
   static const String baseUrl = 'http://10.0.2.2:5217';  // Android emulator → host localhost
   ```
   Physical phone: use your PC's LAN IP, e.g. `http://192.168.1.20:5217` (same Wi-Fi).

4. **Run:**
   ```bash
   flutter pub get
   flutter run
   ```
   Start the backend first: `cd ..\Recycle && dotnet run`.

## Notes
- User-role app; admin lives in the web app (`http://localhost:5217`).
- The Scan screen also has **"Enter code manually"** for when the camera isn't ideal.
- Android cleartext HTTP to `10.0.2.2`/LAN works in debug; for release over plain HTTP add a network-security-config (or serve the API over HTTPS).
