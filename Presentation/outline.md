# Keep It Green — Defense Deck Outline (24 slides · ~25–30 min · hybrid)

Legend: **MSG** = the one thing they remember · **VISUAL** = art/asset · **DATA** = cited number (see facts_sheet.md) · **TIME** target.
Design system: Deep Forest bg for section/impact slides, Paper bg for content; Spring green accents, Sun for numbers; Space Grotesk headings.

---
## ACT I — THE WHY  (problem & stakes · ~5 min)

**1. Title**
- MSG: A recycling machine that pays you back — built for Egypt.
- VISUAL: logo lockup + `keep_it_green_hero.png`; tagline "Recycling that rewards you." Team + university + date.
- TIME: 0:30

**2. The scale of the problem**
- MSG: We're buying plastic faster than we can ever recycle it.
- DATA: **1,000,000 plastic bottles bought every minute** (~500B/yr); **only ~9% recycled**.
- VISUAL: one giant number on Forest bg; small bottle-grid motif.
- TIME: 1:30

**3. Egypt is drowning in it**
- MSG: The crisis is on our doorstep, and it's mostly unrecycled.
- DATA: **~100M tonnes waste/yr** (~80k tons/day); plastic recycling **only 37%**; 2.5M tons plastic/yr.
- VISUAL: Egypt map/silhouette + stat callouts.
- TIME: 1:30

**4. Why people don't recycle**
- MSG: It's not apathy — there's no reward, no convenience, no feedback.
- VISUAL: 3 friction icons (no incentive · inconvenient · invisible impact).
- TIME: 1:00

## ACT II — THE WHAT  (solution & product · ~7 min)

**5. The proven fix: reward it**
- MSG: Where returning a bottle pays, people recycle almost everything.
- DATA: **Germany 98%**, **Norway 97%** container return — via reverse vending (Norway: 3,500 RVMs collect 93%).
- VISUAL: 98% / 97% vs Egypt 37% bar comparison.
- TIME: 1:30

**6. Introducing Keep It Green** ★ 3D
- MSG: AI-powered reverse vending + instant mobile rewards — no deposit law required.
- VISUAL: **live .glb turntable** of the machine (fallback `hero.png`); one-line definition.
- TIME: 1:30

**7. How it works (the ATM flow)**
- MSG: Scan, drop, earn — in under a minute.
- VISUAL: 3-step flow: (1) machine shows QR/code → phone pairs, (2) drop item → AI detects, (3) points land + redeem. Reuse the system-flow diagram.
- TIME: 1:30

**8. Watch it sort** ★ 3D
- MSG: The camera decides, the right bin opens.
- VISUAL: bins `.glb`/`keep_it_green_bins_interior.png`; Plastic→bin A, Aluminum→bin B; servo callout.
- TIME: 1:00

**9. The mobile app**
- MSG: The reward layer lives in your pocket.
- VISUAL: 3–4 app screenshots (welcome · scan/pair · points/home · rewards). Cairo-time, points, redeem.
- TIME: 1:00

**10. The machine screen (kiosk)**
- MSG: A friendly ATM-style flow anyone can use.
- VISUAL: kiosk screenshots (idle QR + keypad · detected · add-another/finish · summary).
- TIME: 0:30

## ACT III — THE HOW  (technical depth · ~7 min)

**11. The AI brain**
- MSG: Real-time computer vision classifies each item with a confidence buffer to avoid mistakes.
- DATA: YOLO detector, 2 classes (Plastic/Aluminum), **~1.2 s stability confirmation**, trained on our dataset (show sample images).
- VISUAL: detection frame with box + confidence; dataset montage.
- TIME: 1:45

**12. System architecture**
- MSG: Five components, one clean data flow.
- VISUAL: architecture diagram (AI machine · .NET+SQL backend · Flutter app · web dashboard · Arduino). X-Machine-Key + JWT labeled.
- TIME: 1:30

**13. Security & trust**
- MSG: Every action is authenticated and role-scoped.
- VISUAL: JWT + roles (User/Admin) · machine-key header · OTP session pairing (nullable until paired).
- TIME: 1:00

**14. Tech stack (and why)**
- MSG: Production-grade, not a prototype.
- VISUAL: stack logos grid — .NET/EF/SQL Server · Flutter/Dart · Ultralytics YOLO/OpenCV · Arduino/servo · PWA.
- TIME: 1:00

**15. Built & tested** (traction proof)
- MSG: It's not slides — it's a working system.
- DATA: 4 platforms live; **23/23 core + 12/12 admin automated tests passing**; installable APK + web + kiosk.
- VISUAL: green test checklist; "scan to try the app" QR.
- TIME: 1:15

## ACT IV — THE BUSINESS  (market & model · ~6 min)

**16. Market opportunity**
- MSG: A proven global market, still absent in Egypt.
- DATA: RVM market **~$1B (2024) → ~$2B by 2030**, CAGR ~8%; Egypt plastic-recycling **$380M→$474M**.
- VISUAL: TAM/SAM/SOM funnel + market growth chart.
- TIME: 1:30

**17. Why Egypt, why now**
- MSG: A young, mobile-first population and a government tailwind.
- DATA: **113M people, median age 24**, **97% mobile connections**, youth 96.7% phone use; national **60% recycling target by 2027**.
- VISUAL: 3 demographic stat cards + policy note.
- TIME: 1:00

**18. Business model**
- MSG: We earn while we clean up.
- DATA: 5 streams — vendor/brand redemptions · **recovered-material resale (Aluminum $1,338/ton vs PET $215)** · machine sponsorship · CSR/ESG contracts · anonymized data. Points map to material value (Al 15 > Plastic 10).
- VISUAL: revenue-streams diagram + unit-economics mini table.
- TIME: 1:30

**19. Competition & our edge**
- MSG: Global players need deposit laws and barcodes — we don't.
- VISUAL: 2×2 or comparison table: TOMRA · Bower · local buy-back vs **Keep It Green** (AI detection · mobile rewards · no-DRS · emerging-market fit).
- TIME: 1:00

**20. Go-to-market**
- MSG: Start where footfall + sustainability budgets meet.
- VISUAL: phased rollout — Pilot (universities, malls, corporate campuses) → City clusters → National; partner logos placeholder.
- TIME: 1:00

## ACT V — THE CLOSE  (impact & ask · ~4 min)

**21. Impact**
- MSG: Every can counts — environmentally and socially.
- DATA: aluminum recycling uses **95% less energy**; material recovered → CO2 avoided; rewards + green jobs.
- VISUAL: before/after or impact stat trio (Forest bg).
- TIME: 1:00

**22. Roadmap**
- MSG: Clear path from campus pilot to national network.
- VISUAL: timeline — now (working system) → more materials/machines → loyalty partners → data platform.
- TIME: 1:00

**23. Team**
- MSG: A full-stack team that shipped a real product.
- VISUAL: 6 cards — Yousef Badr (Lead · AI & Hardware), Eslam Medhat (AI), Ahmed Anwer (AI), Mohanad Ayman (Mobile), Menna Osama (Front End), Shahd El Aswad (Back End).
- TIME: 0:45

**24. Vision + Ask**
- MSG: A greener Egypt, one bottle at a time — here's how you can help.
- VISUAL: Forest bg, logo, the ask (pilot site / funding / mentorship), "Thank you", demo QR.
- TIME: 1:00

---
### Build notes
- ~24 content slides; each ≤ ~20 words on screen — detail goes in speaker notes.
- 3D turntable on slides 6 (& optionally 8) via native `.glb`; `hero.png` poster fallback.
- Charts to generate: 98/97/37 bar (S5), market growth (S16), TAM/SAM/SOM (S16), revenue streams (S18), competition table (S19).
- Reusable diagram: system/ATM flow (S7, S12).
