"""
Keep It Green - CNC / laser cut layout for ONE prototype bin (flat panels).

Generates a 1:1 SVG (units = millimetres) of the 6 flat panels with all the
component holes already placed: SG90 servo window + screw holes, Arduino Nano
mount, USB slot, cable entry, and hinge holes. Butt-jointed + screwed assembly
(router-friendly: no sharp inner finger-joint corners). Cut both bins = run the
file twice / mirror the label.

Edit the parameters, then:  python cnc_layout.py
Output: out/cnc_cut_layout.svg   (open in LightBurn / Inkscape / your CAM tool)

Convention:  RED strokes = cut through,  BLUE = etch/engrave (labels & guides).
"""

import os

# ---- parameters (mm) ------------------------------------------------------
T = 6.0                 # material thickness (CNC wood). 3D-print uses servo_bin.py
IW, ID, IH = 90.0, 90.0, 150.0
OW, OD = IW + 2 * T, ID + 2 * T

SVO_WIN = (12.6, 23.2)  # servo body window  (W x H)
SVO_HOLE_SPAN = 28.0
SVO_SCREW_D = 2.3
NANO = (45.0, 18.0)
USB = (8.0, 6.0)
CABLE_D = 7.0
PIN_D = 3.4
PILOT_D = 3.2
GAP = 16.0              # spacing between panels on the sheet
MARGIN = 14.0

CUT = "#E4002B"
ETCH = "#0057B8"
THIN = 0.25

_parts = []             # (x, y, svg-fragment)


def panel(name, w, h, holes, etch=None):
    """holes: list of ('c',cx,cy,d) circle | ('r',cx,cy,w,h) rect (centre)."""
    s = [f'<rect x="0" y="0" width="{w:.2f}" height="{h:.2f}" rx="2" '
         f'fill="none" stroke="{CUT}" stroke-width="{THIN}"/>']
    for hole in holes:
        if hole[0] == "c":
            _, cx, cy, d = hole
            s.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{d/2:.2f}" '
                     f'fill="none" stroke="{CUT}" stroke-width="{THIN}"/>')
        else:
            _, cx, cy, rw, rh = hole
            s.append(f'<rect x="{cx-rw/2:.2f}" y="{cy-rh/2:.2f}" width="{rw:.2f}"'
                     f' height="{rh:.2f}" rx="1" fill="none" stroke="{CUT}" '
                     f'stroke-width="{THIN}"/>')
    label = etch if etch else name
    s.append(f'<text x="{w/2:.2f}" y="{h-7:.2f}" font-family="Arial" '
             f'font-size="7" fill="{ETCH}" text-anchor="middle">{label}</text>')
    s.append(f'<text x="3" y="9" font-family="Arial" font-size="5" '
             f'fill="{ETCH}">{name}  {w:.0f}x{h:.0f}</text>')
    return w, h, "\n".join(s)


def edge_pilots(w, h, edges="TBLR", n=3):
    """pilot holes along chosen edges, inset 8mm."""
    out, ins = [], 8.0
    if "B" in edges:
        for i in range(n):
            out.append(("c", ins + i * (w - 2 * ins) / (n - 1), h - ins, PILOT_D))
    if "T" in edges:
        for i in range(n):
            out.append(("c", ins + i * (w - 2 * ins) / (n - 1), ins, PILOT_D))
    if "L" in edges:
        for i in range(n):
            out.append(("c", ins, ins + i * (h - 2 * ins) / (n - 1), PILOT_D))
    if "R" in edges:
        for i in range(n):
            out.append(("c", w - ins, ins + i * (h - 2 * ins) / (n - 1), PILOT_D))
    return out


# ---- build the six panels -------------------------------------------------
# BOTTOM  (OW x OD): pilots all round + nano mount holes
bottom_holes = edge_pilots(OW, OD, "TBLR", 3)
nx, ny = OW / 2 - 22, OD - 30
bottom_holes += [("c", nx - NANO[0] / 2, ny, 2.5), ("c", nx + NANO[0] / 2, ny, 2.5),
                 ("r", nx, ny, NANO[0], NANO[1])]  # nano footprint (etch ref via rect)

# FRONT (OW x IH): USB slot low + label
front_holes = edge_pilots(OW, IH, "BLR", 3)
front_holes.append(("r", OW / 2 - 22, IH - 18, USB[0], USB[1]))

# BACK (OW x IH): cable hole + hinge holes along top
back_holes = edge_pilots(OW, IH, "BLR", 3)
back_holes.append(("c", OW / 2, IH - 16, CABLE_D))
back_holes += [("c", 16, 6, PIN_D), ("c", OW - 16, 6, PIN_D)]

# RIGHT (ID x IH): servo window + 2 screw holes (rear-top)
rsx, rsy = ID - 26, 30
right_holes = edge_pilots(ID, IH, "B", 3)
right_holes.append(("r", rsx, rsy, SVO_WIN[0], SVO_WIN[1]))
right_holes += [("c", rsx, rsy - SVO_HOLE_SPAN / 2, SVO_SCREW_D),
                ("c", rsx, rsy + SVO_HOLE_SPAN / 2, SVO_SCREW_D)]

# LEFT (ID x IH): plain
left_holes = edge_pilots(ID, IH, "B", 3)

# LID (OW x OD): hinge holes one edge + servo lever slot
lid_holes = [("c", 16, 6, PIN_D), ("c", OW - 16, 6, PIN_D),
             ("r", OW - 26, 16, 6, 14)]

panels = [
    panel("BOTTOM", OW, OD, bottom_holes),
    panel("LID", OW, OD, lid_holes),
    panel("FRONT", OW, IH, front_holes, etch="FRONT - PLASTIC / ALUMINUM"),
    panel("BACK", OW, IH, back_holes),
    panel("LEFT", ID, IH, left_holes),
    panel("RIGHT (servo)", ID, IH, right_holes),
]

# ---- arrange on a sheet ---------------------------------------------------
x = MARGIN
y = MARGIN
row_h = 0
sheet_w = 0
placed = []
for w, h, frag in panels:
    if x + w + MARGIN > 700 and x > MARGIN:      # wrap row
        x = MARGIN
        y += row_h + GAP
        row_h = 0
    placed.append((x, y, frag))
    x += w + GAP
    row_h = max(row_h, h)
    sheet_w = max(sheet_w, x)
sheet_h = y + row_h + MARGIN
sheet_w += MARGIN

body = "\n".join(
    f'<g transform="translate({px:.2f},{py:.2f})">{frag}</g>' for px, py, frag in placed)

title = (f'<text x="{MARGIN}" y="{MARGIN-4:.0f}" font-family="Arial" '
         f'font-size="6" fill="{ETCH}">Keep It Green bin - CNC cut layout - '
         f'material T={T:.0f}mm - units mm - RED=cut BLUE=etch</text>')

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{sheet_w:.0f}mm" '
       f'height="{sheet_h:.0f}mm" viewBox="0 0 {sheet_w:.2f} {sheet_h:.2f}">\n'
       f'<rect width="{sheet_w:.2f}" height="{sheet_h:.2f}" fill="white"/>\n'
       f'{title}\n{body}\n</svg>\n')

out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(out_dir, exist_ok=True)
path = os.path.join(out_dir, "cnc_cut_layout.svg")
with open(path, "w", encoding="utf-8") as f:
    f.write(svg)
print("wrote", path, f"({sheet_w:.0f} x {sheet_h:.0f} mm)")
