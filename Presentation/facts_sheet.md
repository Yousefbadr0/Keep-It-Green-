# Keep It Green — Presentation Facts Sheet (cited)

> Source of truth for every number in the deck. Each fact notes **[USE]** = where it lands in the pitch.
> Compiled July 2026. Verify a couple of headline figures the night before (some are model estimates).

## 1. The global problem (Act I — Problem)
- **1,000,000 plastic bottles are bought every minute worldwide** (~500 billion/year). [USE: opening hook] — The National / EcoWatch, 2024.
- **Only ~9% of plastic is recycled globally**; the rest is landfilled, burned, or leaks into nature. [USE: the gap] — The National, 2024.
- **PET bottle** global recycling rate **~47%**; **aluminum can ~75%** (most-recycled beverage container). [USE: why our two classes] — Eunomia via Packaging Dive, 2023.
- Aluminum is **infinitely recyclable** and recycling it uses **95% less energy** than virgin production. [USE: environmental payoff] — Aluminum Association.

## 2. Why it matters in Egypt (Act I — local stakes; Act IV — market)
- Egypt generates **~100 million tonnes of waste/year** (~**80,000 tons/day**). [USE: scale] — Waste Management in Egypt (Wikipedia).
- National MSW **recycling rate: 10% (2018) → 37% (2024)**, government **target 60% by 2027**. [USE: momentum + policy tailwind] — Egyptian Streets, 2025.
- **~2.5 million tons of plastic waste/year** (10–14% of total waste). [USE: plastic-specific] — UNIDO / Egyptian Streets.
- Egypt plastic-recycling market: **$380M (2024) → $474M (2030)**. [USE: market growing] — CSR Egypt / GlobeNewswire, 2025.

## 3. The insight: incentives work (Act I→II — the thesis)
Where a reward exists, people return containers. Deposit-Return Schemes (DRS) powered by reverse vending:
- **Germany: >98% container return** (98.4%), ~**135,000 return points**, €0.25/item, since 2003. [USE: proof] — TOMRA.
- **Norway: 97% plastic-bottle recycling**; **3,500 reverse vending machines collect 93%** of packaging; since 1996. [USE: proof + RVM centrality] — TOMRA.
- **Contrast:** no-incentive systems lag badly (global plastic 9%, Egypt 37%). [USE: the "aha" — Egypt has no reward layer yet]

## 4. Market opportunity (Act IV — Market / TAM-SAM-SOM)
- **Reverse Vending Machine market: ~$0.86B–$1.2B (2024) → ~$2.0B by 2030**, CAGR **~7.5–8.5%**. [USE: TAM] — Strategic Market Research / Transparency Market Research.
- Egypt digital readiness (perfect for a mobile-first reward app):
  - **Population 113.6M, median age 24.3** (very young). [USE: SAM/adoption] — DataReportal 2024.
  - **Internet penetration 72.2% (82M users)**; **96% access via mobile**; **110.5M mobile connections (97.3%)**. [USE: mobile-first fit] — DataReportal 2024.
  - **96.7% of youth (18–29) use mobile phones**. [USE: target user] — CAPMAS via Egypt Today.

## 5. Unit economics / business model inputs (Act IV — Business model)
- Recovered-material value in the bin: **Aluminum $1,338/ton**, **PET $215/ton**, glass −$23/ton. [USE: why we reward Aluminum > Plastic, and the material-resale revenue line] — Aluminum Association.
- Our points map to material value: **Plastic = 10 pts, Aluminum = 15 pts** (aluminum worth ~6× PET per ton → higher reward is economically rational).
- Revenue streams to pitch: (1) **vendor/brand partnerships** (promo redemptions = paid placement), (2) **recovered-material resale**, (3) **machine sponsorship / branded wraps**, (4) **CSR/ESG contracts** with corporates & municipalities, (5) **anonymized recycling data**.

## 6. Competition (Act IV — Competition)
- **TOMRA** (Norway) — global RVM leader, ~80% share of DRS machines; hardware-heavy, deposit-law dependent.
- **Bower** (Sweden) — app that rewards recycling via barcode scanning; no detection hardware.
- **Local/informal** — Egypt's Zabaleen collectors, Bekia, Recyclobekia (buy-back apps).
- **Our wedge:** AI camera (no deposit law or barcodes needed) + mobile rewards + ATM-style pairing, built for an emerging market without a national DRS.

## 7. What we built (Act III — Traction) — internal facts, no citation needed
- **4 integrated platforms:** YOLO AI detection (Plastic/Aluminum) · .NET + SQL backend · Flutter mobile app · web dashboard · Arduino-driven machine.
- **ATM-style pairing:** machine shows QR/6-digit code; phone scans or types to pair; live session.
- **Working & tested:** end-to-end automated tests — **23/23 core + 12/12 admin passing**; role-based access (User/Admin), machine-key auth, JWT.
- **Detection confidence buffer** (item confirmed over ~1.2s) to avoid misfires; anti-double-count.
- Cairo-time throughout; installable Android APK + web app + kiosk.

## 8. Team (Team slide)
- **Yousef Badr** — Team Leader · AI & Hardware (system architect; built the end-to-end project)
- **Eslam Medhat** — AI
- **Ahmed Anwer** — AI
- **Mohanad Ayman** — Mobile App
- **Menna Osama** — Front End
- **Shahd El Aswad** — Back End

## 9. Visual & 3D assets (for the deck)
- **3D model (machine):** `Design/keep_it_green_machine.glb` (native-PowerPoint 3D → live Turntable animation), also `.obj/.mtl/.fbx`. Materials already brand-colored (green cap, off-white body).
- **3D model (bins):** `Prototype_Boxes/out/keep_it_green_bins.glb` (+ STLs for the physical CNC/print bins — proof of hardware).
- **Existing renders (stills):** `Design/renders/keep_it_green_hero.png`, `keep_it_green_front.png`, `keep_it_green_cutout.png`; `Prototype_Boxes/renders/keep_it_green_bins.png`, `keep_it_green_bins_interior.png`.
- **Brand:** `design_handoff_keep_it_green/assets/` (logo lockup, leaf logos, app icons); tokens — Spring #18C964, Deep Forest #0C3B2A, Sun #FFC83D, Paper #F6F7F1; fonts Space Grotesk (display) + Hanken Grotesk (body).
- **Product screenshots:** login, kiosk choice/summary, mobile welcome (captured); can capture more.
- **Architecture diagram:** already designed (4-platform ATM flow).

---
### Source links
- https://www.thenationalnews.com/health/2024/09/25/one-million-bottles-of-water-bought-every-minute-around-the-world/
- https://www.ecowatch.com/plastic-bottle-crisis-2450299465.html
- https://www.packagingdive.com/news/aluminum-beverage-can-glass-pet-recycling-rates-eunomia-cop30/805222/
- https://www.aluminum.org/Recycling
- https://en.wikipedia.org/wiki/Waste_management_in_Egypt
- https://egyptianstreets.com/2025/08/11/egypt-accelerates-waste-reforms-and-targets-60-percent-recycling-by-2027/
- https://www.csregypt.com/en/report-egypt-plastic-recycling-market-expected-to-up-from-380-25-m-in-2024-to-reach-473-96-m-by-2030/
- https://www.tomra.com/reverse-vending/media-center/feature-articles/deposit-return-schemes-europe
- https://www.tomra.com/reverse-vending/media-center/feature-articles/germany-deposit-return-scheme
- https://www.strategicmarketresearch.com/market-report/reverse-vending-machine-market
- https://www.transparencymarketresearch.com/reverse-vending-machine-market.html
- https://datareportal.com/reports/digital-2024-egypt
- https://www.egypttoday.com/Article/1/16931/96-7-of-youth-in-the-age-group-18-29
