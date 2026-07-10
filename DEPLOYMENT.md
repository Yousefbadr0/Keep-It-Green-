# Deploy Keep It Green for free (so anyone can try it)

## What actually goes online
You only host **one thing**: the .NET backend. It already serves the **web app** (`wwwroot`) and the **kiosk page** (`/kiosk/`) too, and it needs **one SQL Server database**. So "online" = **1 web app + 1 SQL DB**.

| Part | Where it lives |
|---|---|
| Backend API + Web app + Kiosk page | **Hosted** (public HTTPS URL) |
| SQL Server database | **Hosted** (free MSSQL) |
| Mobile app (APK) | **Distributed** as a download (GitHub Releases) → points at the hosted URL |
| AI machine (Python + camera) | **Stays on your laptop** — it calls the hosted API; use SIMULATE mode for a demo without hardware |

> The AI machine can't be "hosted" (it needs a real camera). For a public trial, people use the **web app** or the **mobile app**; you run the machine live from your laptop against the same hosted backend.

---

## Best-practice choice
Your stack is **.NET 10 + SQL Server (MSSQL)**. Most free hosts only give Postgres/MySQL, so pick a host that supports **MSSQL** — otherwise you'd have to rewrite the data layer.

### ⭐ Option A — MonsterASP.NET (recommended: easiest, free, no card)
Free ASP.NET Core hosting **+ a free MSSQL database + free HTTPS subdomain** (`yourapp.runasp.net`). Perfect match for this project, zero cost, no credit card.

### Option B — Azure free tier (most "professional")
**App Service (F1 free)** + **Azure SQL Database free tier** (genuinely free monthly allowance). Needs a card for identity verification (no charge on free tier). Best if you want it to look enterprise-grade in the defense.

### Option C — Render/Railway/Fly + free Postgres
Only if you **switch the database to PostgreSQL** (change the EF Core provider to Npgsql). More work, but these hosts are modern and Docker-native (a `Dockerfile` is included). Not recommended unless you specifically want it.

---

## Step-by-step (Option A — MonsterASP.NET)

1. **Sign up** at monsterasp.net (free plan). In the panel, create:
   - a **Website** → you get `https://<yourapp>.runasp.net` with free SSL,
   - a **MSSQL database** → copy its **connection string**.

2. **Set secrets on the host** (Environment variables / Connection Strings) — never in code. .NET reads nested keys with a **double underscore**:
   ```
   ConnectionStrings__DefaultConnection = <the MSSQL connection string from the panel>
   jwt__Key      = <a long random secret, 40+ chars>
   jwt__Issuer   = keepitgreen
   jwt__Audience = keepitgreen
   Machine__ApiKey = <a new secret>
   ```
   ⚠️ **Change all three secrets** from the dev defaults (JWT key, Machine key, and the seeded admin password in `Data/SeedData.cs`).

3. **Publish & upload:**
   ```powershell
   cd "D:\Graduation Project\Recycle"
   dotnet publish -c Release -o publish
   ```
   Upload the `publish/` folder via the host's **File Manager / Web Deploy / FTP** (MonsterASP supports all three). Or connect the GitHub repo for auto-deploy.

4. **First run is automatic:** on startup the app applies EF migrations and seeds the admin (`SeedData.InitializeAsync`) — the database creates itself, no manual SQL.

5. **Try it:** open `https://<yourapp>.runasp.net` → the web app. Kiosk demo at `https://<yourapp>.runasp.net/kiosk/?demo`. Admin login `admin@recycle.com` (change the password!).

---

## Point the mobile app at the live server
1. In [Mobile/lib/services/api_service.dart](Mobile/lib/services/api_service.dart) set the default:
   ```dart
   static const String _lanBaseUrl = 'https://<yourapp>.runasp.net';
   ```
   (The in-app **Server settings** screen still lets anyone override it.)
2. Because it's **HTTPS**, cleartext isn't needed anymore. Rebuild:
   ```powershell
   flutter build apk --release
   ```
3. **Distribute the APK for free:** push the repo to GitHub → **Releases** → upload `KeepItGreen.apk` → share the download link (and a QR code). "Anyone can try" = they scan/download, install, and it talks to your live backend. (Alternatively, Firebase App Distribution.)

---

## Best-practice checklist
- ✅ **Secrets in env vars**, never committed; rotate JWT key, `Machine:ApiKey`, and the admin password before going public.
- ✅ **HTTPS only** — free hosts provide it automatically; it also fixes the Android cleartext limitation.
- ✅ **Migrations auto-run on startup** (already wired) — no manual DB setup.
- ⚠️ **Free tiers sleep when idle** (Azure F1 / Render) → the first request is slow (cold start). Add a free **UptimeRobot** monitor pinging the URL every 5 min to keep it warm — this also gives you an uptime page.
- ⚠️ **Free DB size limits** (~0.5–2 GB) — plenty for a demo.
- ✅ **CORS** is already open (`AllowAnyOrigin`) — fine for a demo; tighten to your domain for real production.
- ✅ **Docker option** — a `Recycle/Dockerfile` is included for container hosts (respects `$PORT`).
- ✅ **Back up the DB** the night before the defense (export from the host panel).

---

## Quick "just show the UI" alternative
If you only need people to *see* the web front-end (no live data), you can also drop the Flutter **web build** or the SPA onto **Netlify / Vercel / GitHub Pages / Cloudflare Pages** (all free, drag-and-drop). But the full experience (login, points, redeem) needs the backend — so Option A/B is the real answer.

---

### TL;DR
**MonsterASP.NET** (free .NET + free MSSQL) → set the 3 secrets as env vars → `dotnet publish` and upload → open `https://yourapp.runasp.net`. Point the APK's base URL at that, rebuild, and share it via GitHub Releases. The AI machine stays on your laptop and talks to the same URL.
