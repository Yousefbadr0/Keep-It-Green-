"""
Keep It Green - prototype collection bin (x2) with SG90 servo-actuated flap lid.

A small, portable, single-item bin for the demo. Two of these sit under the
kiosk; the Arduino tells the correct bin's SG90 servo to lift its top flap so
the sorted item drops in, then closes.

Designed for fabrication with accurate component cavities ("true spaces"):
  * SG90 micro-servo panel mount  (body window + 2 screw holes @ 28 mm)
  * Arduino Nano cradle           (45 x 18 mm board + USB cut-out)
  * rear-hinged flap lid          (pin hinge + servo lever tab)
  * wire / cable routing holes
All parametric -> set WALL = 2.5 for 3D printing, or 6.0 for CNC wood.

UNITS: millimetres (1 Blender unit = 1 mm). STL exports are mm, slicer-ready.

Run:
  "C:\\Program Files\\Blender Foundation\\Blender 4.3\\blender.exe" \
      --background --python servo_bin.py
Flags after `--`:  quick = fast preview,  nodummies = hide servo/Nano models.

Outputs in ./out/ :  *.stl (print parts), keep_it_green_bins.glb, .blend, renders/
"""

import bpy
import os
import sys
from math import radians
from mathutils import Vector

QUICK = "quick" in sys.argv
DUMMIES = "nodummies" not in sys.argv

try:
    BASE = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE = os.getcwd()
OUT = os.path.join(BASE, "out")
REN = os.path.join(BASE, "renders")
for d in (OUT, REN):
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------------------
# Parameters (millimetres)
# ---------------------------------------------------------------------------
WALL = 2.5          # wall / floor thickness  (3D print 2.5 ; CNC wood 6.0)
LID_T = 3.0         # lid plate thickness
CLR = 0.4           # fit clearance for component pockets (print tolerance)

IW, ID, IH = 90.0, 90.0, 150.0     # internal width, depth, height
OW, OD = IW + 2 * WALL, ID + 2 * WALL
OH = IH + WALL                      # floor + cavity (open top)

PIN_D = 3.0         # hinge pin diameter (3 mm rod / filament)

# SG90 micro servo (mm)
SVO_BODY = (22.8, 12.2, 22.7)       # body L x W x H
SVO_TAB_SPAN = 32.0                 # length incl. mounting tabs
SVO_HOLE_SPAN = 28.0                # screw-hole centres
SVO_SCREW_D = 2.3                   # clearance for ~M2 self-tappers
SVO_SHAFT_D = 4.8

# Arduino Nano (mm)
NANO = (45.0, 18.0, 1.6)            # PCB L x W x thickness
NANO_BAY_H = 14.0
USB = (8.0, 6.0)                    # mini-USB cut-out W x H

CABLE_D = 7.0       # rear power/cable entry


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _s2l(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lin(col):
    return tuple(_s2l(c) for c in col)


def mat(name, col, metallic=0.0, rough=0.5):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*lin(col), 1.0)
    b.inputs["Metallic"].default_value = metallic
    b.inputs["Roughness"].default_value = rough
    return m


def activate(o):
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o


def box(name, size, center, m=None):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    o = bpy.context.active_object
    o.name = name
    o.scale = size
    activate(o)
    bpy.ops.object.transform_apply(scale=True)
    if m:
        o.data.materials.append(m)
    return o


def cyl(name, d, h, center, axis="Z", m=None, verts=48):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=d / 2.0,
                                        depth=h, location=center)
    o = bpy.context.active_object
    o.name = name
    if axis == "X":
        o.rotation_euler = (0, radians(90), 0)
    elif axis == "Y":
        o.rotation_euler = (radians(90), 0, 0)
    activate(o)
    bpy.ops.object.transform_apply(rotation=True)
    if m:
        o.data.materials.append(m)
    return o


def boolean(target, cutter, op):
    activate(target)
    md = target.modifiers.new("b", "BOOLEAN")
    md.operation = op
    md.object = cutter
    md.solver = "EXACT"
    bpy.ops.object.modifier_apply(modifier=md.name)
    bpy.data.objects.remove(cutter, do_unlink=True)


def diff(target, cutter):
    boolean(target, cutter, "DIFFERENCE")


def union(target, cutter):
    boolean(target, cutter, "UNION")


def engrave(target, text, size, center, depth=0.6):
    bpy.ops.object.text_add(location=center)
    t = bpy.context.active_object
    t.data.body = text
    t.data.size = size
    t.data.align_x = "CENTER"
    t.data.align_y = "CENTER"
    t.data.extrude = depth
    t.rotation_euler = (radians(90), 0, 0)   # face -Y (front)
    activate(t)
    bpy.ops.object.convert(target="MESH")
    diff(target, t)


# ---------------------------------------------------------------------------
# Build one bin
# ---------------------------------------------------------------------------
def build_bin(label, m_body, m_lid, m_servo, m_nano, m_metal, lid_open=False):
    rear = ID / 2.0          # interior rear face (+Y)
    top = IH                 # interior top (z)

    # --- body shell ---------------------------------------------------------
    body = box(f"body_{label}", (OW, OD, OH), (0, 0, OH / 2), m_body)
    # hollow it (open top): cavity rises above the top edge
    cav = box("cav", (IW, ID, IH + 40), (0, 0, WALL + (IH + 40) / 2))
    diff(body, cav)

    # --- servo mounting bracket (interior rib, rear-right) ------------------
    bx = 24.0                                   # bracket plane x
    bracket = box("bracket", (3.0, 34.0, IH - 8),
                  (bx, rear - 17, WALL + (IH - 8) / 2), m_body)
    union(body, bracket)
    # SG90 panel window + 2 screw holes (servo body passes through the rib)
    sx, sy, sz = bx, rear - 16, top - 26
    win = box("win", (8.0, SVO_BODY[1] + CLR, SVO_BODY[0] + CLR), (sx, sy, sz))
    diff(body, win)
    for dz in (-SVO_HOLE_SPAN / 2, SVO_HOLE_SPAN / 2):
        diff(body, cyl("sh", SVO_SCREW_D, 10, (sx, sy, sz + dz), axis="X"))
    # tidy wire pass-through at bracket base
    diff(body, cyl("wp", 6.0, 10, (bx, rear - 16, WALL + 10), axis="X"))

    # --- Arduino Nano cradle (floor, front-left) ---------------------------
    nx, ny = -22.0, -ID / 2 + 4 + NANO[0] / 2    # PCB length along Y
    cradle = box("cradle", (NANO[1] + 2 * 1.8, NANO[0] + 2 * 1.8, NANO_BAY_H),
                 (nx, ny, WALL + NANO_BAY_H / 2), m_body)
    union(body, cradle)
    pocket = box("pocket", (NANO[1] + CLR, NANO[0] + CLR, NANO_BAY_H),
                 (nx, ny, WALL + NANO_BAY_H / 2 + 2))
    diff(body, pocket)
    # USB access slot: through cradle front wall AND box front wall
    usb_y = -OD / 2
    diff(body, box("usb", (USB[0], OD, USB[1]),
                   (nx, usb_y + OD / 2 - 1, WALL + 6)))

    # --- wire / cable holes -------------------------------------------------
    diff(body, cyl("cable", CABLE_D, 4 * WALL, (0, rear + WALL / 2, WALL + 12),
                   axis="Y"))

    # --- rear hinge ears on the body ---------------------------------------
    hz = top + 2.0                               # hinge axis height
    hy = rear + WALL / 2
    for hx in (-(OW / 2 - 3), (OW / 2 - 3)):
        ear = box("ear", (6.0, 8.0, 8.0), (hx, hy, hz), m_body)
        union(body, ear)
        diff(body, cyl("eh", PIN_D + 0.6, 12, (hx, hy, hz), axis="X"))

    # --- engraved brand label on the front ---------------------------------
    engrave(body, label, 9.0, (0, -OD / 2, IH * 0.55))

    # --- lid (rear-hinged flap) --------------------------------------------
    lid = box(f"lid_{label}", (OW, OD, LID_T), (0, 0, top + LID_T / 2 + 0.5), m_lid)
    rim = box("rim", (IW - CLR, ID - CLR, 4.0), (0, 0, top - 1.0), m_lid)
    union(lid, rim)
    # lid hinge ears (inboard of the body ears) + lever tab for the servo horn
    for hx in (-(OW / 2 - 10), (OW / 2 - 10)):
        le = box("le", (6.0, 8.0, 8.0), (hx, hy, hz), m_lid)
        union(lid, le)
        diff(lid, cyl("lh", PIN_D + 0.6, 12, (hx, hy, hz), axis="X"))
    tab = box("tab", (4.0, 5.0, 20.0), (bx, rear - 16, top - 8), m_lid)
    union(lid, tab)

    # hinge the lid about the rear pin axis
    bpy.context.scene.cursor.location = (0, hy, hz)
    activate(lid)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    if lid_open:
        lid.rotation_euler = (radians(-72), 0, 0)
    bpy.context.scene.cursor.location = (0, 0, 0)

    # --- hinge pin (printable / or use a 3 mm rod) -------------------------
    pin = cyl(f"pin_{label}", PIN_D, OW + 4, (0, hy, hz), axis="X", m=m_metal)

    parts = {"body": body, "lid": lid, "pin": pin}

    # --- visual-only component dummies (excluded from STL) -----------------
    if DUMMIES:
        # SG90: body through the bracket, shaft + horn on the +x side
        d = box(f"dummy_servo_{label}", (SVO_BODY[2], SVO_BODY[1], SVO_BODY[0]),
                (bx - SVO_BODY[2] / 2, sy, sz), m_servo)
        cyl(f"dummy_shaft_{label}", SVO_SHAFT_D, 6, (bx + 3, sy, sz + 6),
            axis="X", m=m_servo)
        box(f"dummy_horn_{label}", (1.6, 4.0, 26.0), (bx + 5, sy, sz + 10), m_servo)
        # Arduino Nano in its cradle
        box(f"dummy_nano_{label}", (NANO[1], NANO[0], NANO[2]),
            (nx, ny, WALL + 4), m_nano)
        box(f"dummy_usb_{label}", (USB[0], 9, 4),
            (nx, -ID / 2 + 3, WALL + 6), m_metal)
    return parts


# ---------------------------------------------------------------------------
# Scene / stage
# ---------------------------------------------------------------------------
def look_at(o, target):
    d = Vector(target) - o.location
    o.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def stage_and_render():
    sc = bpy.context.scene
    sc.unit_settings.system = "METRIC"
    sc.unit_settings.length_unit = "MILLIMETERS"

    # ground
    bpy.ops.mesh.primitive_plane_add(size=2000, location=(0, 0, 0))
    bpy.context.active_object.data.materials.append(
        mat("ground", (0.62, 0.64, 0.66), rough=0.25))

    # lights (Sun lamps: distance-independent, easy at mm scale)
    for loc, e in (((-220, -260, 320), 4.0),
                   ((260, -200, 200), 1.6),
                   ((60, 280, 300), 2.6)):
        bpy.ops.object.light_add(type="SUN", location=loc)
        L = bpy.context.active_object
        L.data.energy = e
        L.data.angle = radians(8)
        look_at(L, (0, 0, 80))

    w = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
    sc.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes.get("Background")
    bg.inputs[0].default_value = (*lin((0.82, 0.85, 0.89)), 1.0)
    bg.inputs[1].default_value = 0.6

    sc.render.engine = "CYCLES"
    try:
        sc.cycles.device = "CPU"
        sc.cycles.samples = 16 if QUICK else 110
        sc.cycles.use_denoising = True
    except Exception as e:
        print("cycles note:", e)
    try:
        sc.view_settings.view_transform = "AgX"
        sc.view_settings.look = "AgX - High Contrast"
    except Exception:
        pass
    sc.render.resolution_x = 1000 if QUICK else 1700
    sc.render.resolution_y = 760 if QUICK else 1150
    sc.render.image_settings.file_format = "PNG"

    x_open = OW / 2 + 12          # the open (Aluminum) bin's x position
    bpy.ops.object.camera_add()
    cam = bpy.context.active_object
    sc.camera = cam

    def render_view(name, loc, target, lens):
        cam.location = loc
        cam.data.lens = lens
        look_at(cam, target)
        sc.render.filepath = os.path.join(REN, name)
        bpy.ops.render.render(write_still=True)
        print("render:", name)

    render_view("keep_it_green_bins.png", (360, -470, 330), (0, 0, 85), 52)
    render_view("keep_it_green_bins_interior.png",
                (x_open + 60, -250, 250), (x_open, 15, 95), 46)
    print("render saved")


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------
def export_stl(obj, name):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    path = os.path.join(OUT, name + ".stl")
    try:
        bpy.ops.wm.stl_export(filepath=path, export_selected_objects=True,
                              global_scale=1.0)
    except Exception:
        bpy.ops.export_mesh.stl(filepath=path, use_selection=True,
                                global_scale=1.0)
    print("STL:", path)


def export_all(all_parts):
    # one of each unique print part (+ both labelled bodies)
    export_stl(all_parts["PLASTIC"]["body"], "bin_body_PLASTIC")
    export_stl(all_parts["ALUMINUM"]["body"], "bin_body_ALUMINUM")
    export_stl(all_parts["PLASTIC"]["lid"], "bin_lid")
    export_stl(all_parts["PLASTIC"]["pin"], "bin_hinge_pin")

    # assembled pair (with component models) for viewing / PowerPoint
    bpy.ops.object.select_all(action="DESELECT")
    for o in bpy.data.objects:
        if o.type == "MESH" and o.name != "Plane":
            o.select_set(True)
    glb = os.path.join(OUT, "keep_it_green_bins.glb")
    bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB",
                              use_selection=True)
    print("GLB:", glb)


def main():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

    m_paper = mat("paper", (0.965, 0.969, 0.945), rough=0.35)
    m_spring = mat("spring", (0.094, 0.788, 0.392), rough=0.4)
    m_mint = mat("mint", (0.863, 0.945, 0.886), rough=0.4)
    m_forest = mat("forest", (0.047, 0.231, 0.165), rough=0.4)
    m_servo = mat("servo", (0.10, 0.22, 0.62), rough=0.45)
    m_nano = mat("nano", (0.05, 0.22, 0.32), rough=0.5)
    m_metal = mat("metal", (0.78, 0.80, 0.83), metallic=1.0, rough=0.3)

    def move_suffix(suffix, dx):
        for o in bpy.data.objects:
            if o.name.endswith(suffix):
                o.location.x += dx

    dx = OW / 2 + 12
    all_parts = {}
    # Plastic bin (spring green) - closed, used for the clean print exports
    all_parts["PLASTIC"] = build_bin("PLASTIC", m_spring, m_forest, m_servo,
                                     m_nano, m_metal, lid_open=False)
    move_suffix("PLASTIC", -dx)
    # Aluminum bin (mint) - lid open to show the servo mechanism in the hero
    all_parts["ALUMINUM"] = build_bin("ALUMINUM", m_mint, m_forest, m_servo,
                                      m_nano, m_metal, lid_open=True)
    move_suffix("ALUMINUM", dx)

    stage_and_render()

    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(BASE,
                                                      "keep_it_green_bins.blend"))
    export_all(all_parts)
    print("done; parts in", OUT)


if __name__ == "__main__":
    main()
