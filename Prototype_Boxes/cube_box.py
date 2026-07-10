"""
Keep It Green - 100 x 100 x 100 mm finger-jointed cube with a SERVO-DRIVEN LID.

Proof-of-concept sorting bin. Laser/CNC cut, 3 mm material. An open-top
finger-jointed box (bottom + 4 walls) plus a separate hinged LID that an SG90
micro-servo lifts open and closes.

MECHANISM (why it's built this way):
  Flat-pack pin hinges can't be laser-cut (the pin would lie in the sheet
  plane). So the LID pivots on the servo's own shaft:
    * RIGHT wall  -> SG90 body screwed in; shaft points inward = hinge axis.
    * LEFT  wall  -> a screw at the same height = the coaxial pivot bearing.
    * Two small BRACKETS glue under the lid's back corners and ride those two
      pivots. Rotating the servo horn lifts / lowers the whole lid.
  Hinge axis runs along the BACK-TOP edge.

  python cube_box.py   ->   out/keepitgreen_cube_<LABEL>.dxf (+ .svg, + json)
Layers:  CUT (red) cut-through,  ENGRAVE (blue) surface mark / text.
"""

import os
import json

# ---- parameters (mm) ------------------------------------------------------
L = 100.0
T = 3.0
N = 5
FW = (L - 2 * T) / N
DOGBONE = True
DB_D = 1.8

SVO_WIN = (12.6, 23.2)       # servo window on the right wall (u=depth, v=height)
SVO_SCREW_D = 2.3
SVO_SCREW_SPAN = 28.0
PIVOT_D = 3.6                # left-wall pivot hole
WIRE_D = 6.0
CABLE_D = 7.0
HB = 17.0                    # hinge distance from the back wall
HZ = L - 20.0               # hinge / servo centre height

TAB, SLOT = "tab", "slot"
H_PAT = [TAB, SLOT, TAB, SLOT, TAB]
V_FB = [TAB, SLOT, TAB, SLOT, TAB]
V_LR = [SLOT, TAB, SLOT, TAB, SLOT]
OWNER = [SLOT, TAB, SLOT, TAB, SLOT]


# ---- vector helpers -------------------------------------------------------
def add(a, b): return (a[0] + b[0], a[1] + b[1])
def mul(a, s): return (a[0] * s, a[1] * s)


def run(start, d, inw, pat, dogs):
    pts, cur = [], start
    for k in pat:
        if k == SLOT:
            a = add(cur, mul(inw, T)); b = add(a, mul(d, FW)); c = add(cur, mul(d, FW))
            pts += [a, b, c]; cur = c
            if dogs is not None:
                dogs += [a, b]
        else:
            cur = add(cur, mul(d, FW)); pts.append(cur)
    return pts, cur


def owner_panel(dogs):
    corners = [(0, 0), (L, 0), (L, L), (0, L)]
    dirs = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    inws = [(0, 1), (-1, 0), (0, -1), (1, 0)]
    pts = []
    for i in range(4):
        P0, d, inw = corners[i], dirs[i], inws[i]
        cur = add(P0, mul(d, T)); pts += [P0, cur]
        seg, cur = run(cur, d, inw, OWNER, dogs); pts += seg
        pts.append(add(cur, mul(d, T)))
    return pts


def wall_open_top(vpat, dogs):
    """Open-top wall: bottom + vertical edges fingered, top edge plain, all
    four corners cut T x T."""
    pts = [(T, 0)]
    seg, _ = run((T, 0), (1, 0), (0, 1), H_PAT, dogs); pts += seg          # bottom
    pts += [(L - T, T), (L, T)]                                            # BR cut
    seg, _ = run((L, T), (0, 1), (-1, 0), vpat, dogs); pts += seg          # right
    pts += [(L - T, L - T), (L - T, L)]                                    # TR cut
    pts += [(T, L)]                                                        # top (plain)
    pts += [(T, L - T), (0, L - T)]                                        # TL cut
    seg, _ = run((0, L - T), (0, -1), (1, 0), vpat, dogs); pts += seg      # left
    pts += [(T, T), (T, 0)]                                                # BL cut
    return pts


def rect(cx, cy, w, h):
    return [(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2),
            (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)]


# ---- assemble the part list ----------------------------------------------
def build_parts(label):
    parts = []

    def P(name, outline, w, h, circles=None, rects=None, texts=None, dogs=None):
        parts.append({"name": name, "outline": outline, "w": w, "h": h,
                      "circles": circles or [], "rects": rects or [],
                      "texts": texts or [], "dogs": dogs or []})

    dB = []; P("BOTTOM", owner_panel(dB), L, L, dogs=dB)

    dF = []
    P("FRONT (label)", wall_open_top(V_FB, dF), L, L,
      texts=[(L / 2, L / 2, 13, label), (L / 2, L / 2 + 15, 5, "KEEP IT GREEN")],
      dogs=dF)

    dK = []
    P("BACK (cable)", wall_open_top(V_FB, dK), L, L,
      circles=[(L / 2, 18, CABLE_D / 2)], dogs=dK)

    dR = []
    cx = L - HB
    P("RIGHT (servo)", wall_open_top(V_LR, dR), L, L,
      circles=[(cx, HZ + SVO_SCREW_SPAN / 2, SVO_SCREW_D / 2),
               (cx, HZ - SVO_SCREW_SPAN / 2, SVO_SCREW_D / 2),
               (cx, HZ - 22, WIRE_D / 2)],
      rects=[(cx, HZ, SVO_WIN[0], SVO_WIN[1])], dogs=dR)

    dL = []
    P("LEFT (pivot)", wall_open_top(V_LR, dL), L, L,
      circles=[(L - HB, HZ, PIVOT_D / 2)], dogs=dL)

    # LID: flat plate, hinge brackets glue at the back, grip notch at the front
    P("LID", rect(L / 2, L / 2, L, L), L, L,
      circles=[(L / 2, 12, 11),                                   # finger grip
               (14, L - 12, 1.6), (26, L - 12, 1.6),             # left bracket tabs
               (L - 14, L - 12, 1.6), (L - 26, L - 12, 1.6)],    # right bracket tabs
      texts=[(L / 2, L / 2, 9, label)])

    # HINGE BRACKET x2 : glue under the lid back corners, ride the pivots
    for tag in ("BRACKET-R (horn)", "BRACKET-L (pivot)"):
        P(tag, rect(11, 9, 22, 18), 22, 18,
          circles=[(11, 12, 5.2 / 2), (5, 3.5, 1.6), (17, 3.5, 1.6)])

    return parts


# ---- layout ---------------------------------------------------------------
def layout(parts):
    x, y, rowh, placed, maxw = 12.0, 12.0, 0.0, [], 0.0
    for p in parts:
        if x + p["w"] + 12 > 380 and x > 12:
            x = 12.0; y += rowh + 14; rowh = 0.0
        placed.append((x, y, p)); x += p["w"] + 14
        rowh = max(rowh, p["h"]); maxw = max(maxw, x)
    return placed, maxw + 6, y + rowh + 14


# ---- emitters -------------------------------------------------------------
def dxf(placed, path):
    e = []

    def poly(points, layer):
        e.append("0\nPOLYLINE\n8\n%s\n66\n1\n70\n1" % layer)
        for (px, py) in points:
            e.append("0\nVERTEX\n8\n%s\n10\n%.3f\n20\n%.3f" % (layer, px, py))
        e.append("0\nSEQEND")

    def circle(cx, cy, r, layer):
        e.append("0\nCIRCLE\n8\n%s\n10\n%.3f\n20\n%.3f\n40\n%.3f" % (layer, cx, cy, r))

    def text(cx, cy, hgt, s):
        e.append("0\nTEXT\n8\nENGRAVE\n10\n%.3f\n20\n%.3f\n40\n%.3f\n1\n%s\n72\n1\n11\n%.3f\n21\n%.3f"
                 % (cx, cy, hgt, s, cx, cy))

    for (ox, oy, p) in placed:
        poly([(px + ox, py + oy) for (px, py) in p["outline"]], "CUT")
        for (cx, cy, r) in p["circles"]:
            circle(ox + cx, oy + cy, r, "CUT")
        for (cx, cy, w, h) in p["rects"]:
            poly([(ox + x, oy + y) for (x, y) in rect(cx, cy, w, h)], "CUT")
        for (dx, dy) in p["dogs"]:
            circle(ox + dx, oy + dy, DB_D / 2, "CUT")
        for (tx, ty, hgt, s) in p["texts"]:
            text(ox + tx, oy + ty, hgt, s)

    layers = ("0\nLAYER\n2\nCUT\n70\n0\n62\n1\n6\nCONTINUOUS\n"
              "0\nLAYER\n2\nENGRAVE\n70\n0\n62\n5\n6\nCONTINUOUS")
    with open(path, "w") as f:
        f.write("0\nSECTION\n2\nHEADER\n9\n$ACADVER\n1\nAC1009\n0\nENDSEC\n"
                "0\nSECTION\n2\nTABLES\n0\nTABLE\n2\nLAYER\n70\n2\n" + layers +
                "\n0\nENDTAB\n0\nENDSEC\n0\nSECTION\n2\nENTITIES\n" +
                "\n".join(e) + "\n0\nENDSEC\n0\nEOF\n")


def svg(placed, sw, sh, path):
    def fy(v): return sh - v
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{sw:.0f}mm" height="{sh:.0f}mm" viewBox="0 0 {sw:.1f} {sh:.1f}">',
         f'<rect width="{sw:.1f}" height="{sh:.1f}" fill="white"/>']
    for (ox, oy, p) in placed:
        pd = " ".join(f'{ox+px:.2f},{fy(oy+py):.2f}' for (px, py) in p["outline"])
        s.append(f'<polygon points="{pd}" fill="#eef7ef" stroke="#E4002B" stroke-width="0.4"/>')
        for (cx, cy, r) in p["circles"]:
            s.append(f'<circle cx="{ox+cx:.2f}" cy="{fy(oy+cy):.2f}" r="{r:.2f}" fill="none" stroke="#E4002B" stroke-width="0.4"/>')
        for (cx, cy, w, h) in p["rects"]:
            s.append(f'<rect x="{ox+cx-w/2:.2f}" y="{fy(oy+cy)-h/2:.2f}" width="{w:.2f}" height="{h:.2f}" fill="none" stroke="#E4002B" stroke-width="0.4"/>')
        for (dx, dy) in p["dogs"]:
            s.append(f'<circle cx="{ox+dx:.2f}" cy="{fy(oy+dy):.2f}" r="{DB_D/2:.2f}" fill="none" stroke="#E4002B" stroke-width="0.3"/>')
        for (tx, ty, hgt, st) in p["texts"]:
            s.append(f'<text x="{ox+tx:.2f}" y="{fy(oy+ty)+hgt/2:.2f}" font-family="Arial" font-size="{hgt}" fill="#0057B8" text-anchor="middle">{st}</text>')
        s.append(f'<text x="{ox+3:.2f}" y="{fy(oy+p["h"])+7:.2f}" font-family="Arial" font-size="4.2" fill="#0057B8">{p["name"]}</text>')
    s.append("</svg>")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(s))


def main():
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    os.makedirs(out, exist_ok=True)
    for label in ("PLASTIC", "ALUMINUM"):
        parts = build_parts(label)
        placed, sw, sh = layout(parts)
        base = os.path.join(out, f"keepitgreen_cube_{label}")
        dxf(placed, base + ".dxf")
        svg(placed, sw, sh, base + ".svg")
        json.dump([{"name": p["name"], "outline": p["outline"], "w": p["w"], "h": p["h"]}
                   for p in parts], open(base + "_panels.json", "w"))
        print(f"wrote {label}: sheet {sw:.0f} x {sh:.0f} mm ->", base + ".dxf")


if __name__ == "__main__":
    main()
