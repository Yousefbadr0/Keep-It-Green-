# Keep It Green — prototype collection bins (servo-actuated)

---

## ⭐ CNC / laser cube (the file for the workshop) — `cube_box.py`

A **100 × 100 × 100 mm finger-jointed cube** in **3 mm** material with a
**servo-driven lid**. This is the proof-of-concept the CNC shop cuts.

**Give the shop:** `out/keepitgreen_cube_PLASTIC.dxf` and
`out/keepitgreen_cube_ALUMINUM.dxf` (universal **DXF R12**; he can *Save As DWG*
if he insists — same geometry). Layers: **CUT** (red) = cut through,
**ENGRAVE** (blue) = surface mark / labels. `.svg` twins are for previewing.

**Parts per box (all on one sheet):** BOTTOM, FRONT (label), BACK (cable hole),
RIGHT (SG90 mount), LEFT (pivot), LID, + 2 hinge BRACKETs.

**The lid mechanism (opens/closes with the motor):**
Laser/CNC can't cut a normal pin hinge (the pin would lie flat in the sheet),
so the **lid pivots on the SG90's own shaft**:
1. **SG90** screws into the **RIGHT** wall window (2 × M2), shaft pointing
   inward — this is the hinge axis, along the back-top edge.
2. A screw through the **LEFT** wall (pivot hole) is the coaxial bearing.
3. The two small **BRACKETs** glue under the lid's back corners and ride those
   two pivots; the right one couples to the servo horn.
4. Servo sweeps → lid lifts open ~65° → item drops in → lid closes.
Wiring is unchanged from the AI kiosk: Arduino sends `P` / `A`, the matching
servo sweeps.

**Best-practice details baked in:** finger joints sized exactly to 3 mm, top &
bottom own the corners, **dog-bone overcuts** at inner corners (so it works on a
router *and* a laser), separate CUT/ENGRAVE layers, engraved PLASTIC / ALUMINUM
+ KEEP IT GREEN. Verified by folding the panels into a cube in 3D — it closes
cleanly. Regenerate with `python cube_box.py` (tweak `L`, `T`, `N` at the top).

Preview render: `blender --background --python make_cube_preview.py` (`-- alu`).

---

## (Earlier) 3D-printed bins — `servo_bin.py`

Two small, portable bins that sit under the kiosk. The Arduino reads the YOLO
result, tells the **correct bin's SG90 servo** to lift its top flap, the sorted
item drops in, and the flap closes. Brand-coloured: **Plastic = spring green**,
**Aluminum = mint**, both with a **deep-forest lid**.

## Files

| File | What it is |
|---|---|
| `servo_bin.py` | Parametric Blender model → renders, `.glb`, and **print-ready STL** |
| `cnc_layout.py` | Generates `out/cnc_cut_layout.svg` — flat panels for **CNC/laser wood** |
| `out/bin_body_PLASTIC.stl`, `out/bin_body_ALUMINUM.stl` | The two bin bodies (engraved labels) |
| `out/bin_lid.stl` | The flap lid (print 2×) |
| `out/bin_hinge_pin.stl` | Hinge pin (or use a 3 mm rod / filament) |
| `out/keep_it_green_bins.glb` | Assembled pair **with servo + Nano models** — drop into slides |
| `out/cnc_cut_layout.svg` | 1:1 cut layout (RED = cut, BLUE = etch) |
| `keep_it_green_bins.blend` | Editable source |

## Dimensions (default)

- **Bin:** 90 × 90 × 150 mm internal → ~95 × 95 × 153 mm external (3D-print walls).
  Holds a can / small bottle. For a full 0.5 L bottle, raise `IH` to ~210.
- All parametric at the top of `servo_bin.py`.

## Component "true spaces" (with fit clearance)

| Part | Modelled size | Pocket |
|---|---|---|
| **SG90 servo** | 22.8 × 12.2 × 22.7 mm, tabs @ 28 mm | body window 23.2 × 12.6 mm + 2 × ⌀2.3 screw holes @ 28 mm |
| **Arduino Nano** | 45 × 18 mm board | floor cradle 45.4 × 18.4 mm + USB cut-out 8 × 6 mm |
| **Hinge pin** | ⌀3 mm rod | ⌀3.4 mm ears on body + lid |
| **Cable entry** | — | ⌀7 mm in the back wall |

`CLR = 0.4 mm` clearance is applied to every pocket — tweak for your printer.

## 3D printing (recommended)

- `WALL = 2.5` in `servo_bin.py` (default). Re-run to regenerate STLs.
- Suggested: PLA/PETG, 0.2 mm layers, 3 walls, 15–20 % infill, no supports
  (the lid prints flat; the body prints open-side-up).
- Print: `bin_body_*` ×1 each, `bin_lid` ×2, pin ×2 (or use rod).

## CNC / laser wood

- Set `T` in `cnc_layout.py` (default 6 mm), run `python cnc_layout.py`.
- Butt-jointed + screwed (router-friendly — no sharp inner corners).
- Open `out/cnc_cut_layout.svg` in LightBurn/Inkscape/your CAM tool.

## Assembly & wiring

1. Screw the **SG90** into the right-wall window (2 × M2 self-tappers).
2. Drop the **Nano** into the floor cradle; USB faces the front slot.
3. Fit the **lid** with the **pin** through the rear ears; screw the servo
   horn to the lid's lever tab so rotating the servo lifts the flap.
4. Wire: servo signal → an Arduino D-pin (e.g. D9 / D10), servo V+/GND →
   5 V/GND; route the servo lead down to the Nano, power in via the rear hole.
5. Arduino reads `P` / `A` over serial (per the AI kiosk) and sweeps the
   matching servo open→pause→closed.

## Regenerate

```bash
"C:\Program Files\Blender Foundation\Blender 4.3\blender.exe" --background --python servo_bin.py
python cnc_layout.py
```
Add `-- quick` for a fast preview render, `-- nodummies` to hide the servo/Nano models.
