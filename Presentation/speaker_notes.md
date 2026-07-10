# Keep It Green — Speaker Notes & Q&A (≈25–30 min)

**Flow:** Problem (5) → Solution & product (7) → Technology (7) → Business (6) → Close (4).
**Golden rule:** one message per slide, say the number, then the "so what." Don't read the slide.

---
## ACT I — THE WHY (≈5 min)

**1 · Title (0:30)** — "Good morning. We're Keep It Green. We built a recycling machine that pays you back — AI-powered reverse vending, made for Egypt." Introduce the team in one line. Set energy.

**2 · The problem (1:30)** — "Every minute, the world buys a million plastic bottles — half a trillion a year. And only about 9% is ever recycled." Let the number land. "This isn't a habit problem — it's a system problem."

**3 · Egypt (1:30)** — "Here at home it's stark: 100 million tonnes of waste a year, and plastic recycling still sits around 37%." Then the hopeful pivot: "The government wants 60% by 2027 — the pressure and the policy are both moving."

**4 · Why people don't recycle (1:00)** — "Ask anyone why they don't recycle. It's never 'I don't care.' It's: there's no reward, it's inconvenient, and you never see your impact. Fix those three and behavior changes."

## ACT II — THE WHAT (≈7 min)

**5 · Rewards work (1:30)** — "We know this works. Germany returns 98% of its containers. Norway, 97%. The difference isn't culture — it's a reward, delivered through reverse vending machines. Egypt simply has no reward layer yet. That gap is our opportunity."

**6 · Keep It Green + 3D (1:30)** — Play the 3D tour. "This is our machine. You place a bottle or can, the camera identifies it, and points hit your phone instantly — no deposit law, no barcodes, no staff." Let the rotation/zoom do the talking.

**7 · How it works (1:30)** — Walk the three steps. "Pair like an ATM — scan a QR or type a 6-digit code. Drop the item; the AI confirms it. Points land and you redeem them in the app. Under a minute, start to finish."

**8 · Watch it sort (1:00)** — "Once the camera decides, an Arduino opens the correct compartment — Plastic to one bin, Aluminum to the other. This is a working hardware prototype, not a render."

**9 · Mobile app (1:00)** — "The reward layer lives in the app: scan and pair, watch points land in Cairo time, redeem for vendor rewards — and the promo code is only revealed after you redeem."

**10 · Kiosk (0:30)** — "The machine screen is deliberately ATM-simple. Place an item… and finish with a clear reward summary — points earned and your new total."

## ACT III — THE HOW (≈7 min)

**11 · AI (1:45)** — "The brain is a YOLO computer-vision model that classifies each item live. Two classes — plastic and aluminum. And a confidence buffer: the item has to stay confidently detected for about 1.2 seconds before it counts, so a glance or a wrong read never triggers a reward." Mention the dataset.

**12 · Architecture (1:30)** — "Five components, one flow. The AI machine, a .NET backend on SQL Server, the Flutter app, the web dashboard, and the Arduino hardware. Crucially, nothing touches the database directly — every request is authenticated through the backend."

**13 · Security (1:00)** — "Every action is authenticated and role-scoped. Users get JWTs; admins and users are separated; machines carry a secret key; and a detection is only ever credited to the user paired to that live session."

**14 · Tech stack (1:00)** — "This is a production-grade stack, not a class prototype." Name each layer briefly and why it was chosen.

**15 · Built & tested (1:15)** — "And it's real. All five components run. We wrote automated end-to-end tests — 23 of 23 on the core flow, 12 of 12 on admin — and they pass: register, pair, detect, earn, redeem, all verified. There's an installable APK, a web app, and the kiosk."

## ACT IV — THE BUSINESS (≈6 min)

**16 · Market (1:30)** — "The reverse-vending market is about a billion dollars today, roughly two by 2030. Egypt's recycling market is growing too. Our beachhead is Cairo — universities, malls, and corporate campuses."

**17 · Why Egypt now (1:00)** — "The timing is ideal: 113 million people, median age 24, 97% on mobile. A mobile-first reward app fits perfectly — and the 60% national target pushes with us."

**18 · Business model (1:30)** — "We make money while we clean up: vendors pay for the promos users redeem, we resell recovered material, plus sponsorship, ESG contracts, and data. And notice — aluminum is worth $1,338 a ton versus $215 for PET. That's exactly why we reward aluminum more. The points mirror real value."

**19 · Competition (1:00)** — "The global leaders need deposit laws and barcodes. We need neither — our camera reads the item directly. That makes us the fit for an emerging market that has no national deposit scheme."

**20 · Go-to-market (1:00)** — "We start where footfall meets sustainability budgets — pilot on campuses and in malls, densify into city clusters, then scale with municipality and ESG contracts."

## ACT V — THE CLOSE (≈4 min)

**21 · Impact (1:00)** — "The payoff is real: recycling aluminum uses 95% less energy than making it new. Material goes back into the economy instead of the Nile, and the machines create rewards and green jobs."

**22 · Roadmap (1:00)** — "From here: more materials, more machines, brand partners, and ultimately a recycling-data platform for cities."

**23 · Team (0:45)** — Introduce each member and their role. Keep it warm and quick.

**24 · Vision + Ask (1:00)** — "A greener Egypt, one bottle at a time. We're looking for a pilot site, funding, and mentorship to get there. Thank you — we'd love your questions."

---
## Q&A — likely questions & strong answers

**How accurate is the AI, and what about items it hasn't seen?** Two-class model with a confidence threshold plus a 1.2-second stability buffer, so low-confidence or unfamiliar items are simply rejected rather than mis-rewarded. Captured images feed continuous retraining.

**What stops fraud — fake Q', empty bottles, gaming the points?** Detections are only credited to the paired session; the machine authenticates with a secret key; and a cooldown plus "item must clear before the next counts" prevents double-counting. Weight/volume sensing is on the roadmap.

**Why not just use barcodes like Bower?** Barcodes require a clean, scannable label and a product database. Our camera classifies the material directly — it works on crushed, label-less, or unfamiliar containers, which is the real-world case in Egypt.

**How is this different from TOMRA?** TOMRA depends on national deposit laws and expensive hardware. We reward through the app without a deposit scheme, at a fraction of the cost — designed for markets that don't have DRS.

**What's the unit economics / how do you make money?** Vendor-funded rewards and recovered-material resale (aluminum ~$1,338/ton) are the core; sponsorship, ESG contracts, and data add to it. Aluminum-heavy streams are cash-positive on material alone.

**Why should a vendor pay you?** Measurable, sustainability-aligned footfall and redemptions — a green loyalty channel to a young, mobile audience, with data to prove ROI.

**Is the hardware real or simulated?** Real: Arduino-driven servos open the correct bin, and there's a working machine program running the camera and UI. We also have 3D-printable/CNC bin parts.

**How do you scale manufacturing and placement?** Start with a few pilot units on campuses/malls, standardize the enclosure (we have the CAD), and grow placement through property and ESG partnerships.

**What about connectivity/offline?** The machine talks to the backend over the network; sessions are short and idempotent. Offline queueing of transactions is a straightforward addition.

**Security of user data?** JWT auth, role separation, no direct DB access, and no sensitive personal data stored beyond account basics. Times are handled in Cairo time; secrets are rotated before deployment.

**What's the biggest risk, honestly?** Placement economics and vendor supply at scale. We de-risk with a campus pilot to prove redemption rates before committing to hardware volume.
