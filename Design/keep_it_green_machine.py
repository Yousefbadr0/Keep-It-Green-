"""
Keep It Green - smart recycling machine (reverse-vending kiosk).

Procedural Blender model + render setup. Inspired by German TOMRA reverse
vending machines, themed for the "Keep It Green" graduation project:
illuminated insertion ring, touchscreen, AI-vision camera module, two sorted
compartments (Plastic / Aluminum), coin/receipt tray, LED accents, leaf logo.

Run (build + render):
    "C:\\Program Files\\Blender Foundation\\Blender 4.3\\blender.exe" \
        --background --python keep_it_green_machine.py

Fast preview (low samples / small image):
    ... --python keep_it_green_machine.py -- quick

Outputs: ./renders/*.png  and  ./keep_it_green_machine.blend
Open the .blend in Blender to orbit, tweak colours, or re-render.
"""

import bpy
import os
import sys
from math import radians
from mathutils import Vector

# ----------------------------------------------------------------------------
# Config
# ----------------------------------------------------------------------------
QUICK = "quick" in sys.argv
BOTTLE = "nobottle" not in sys.argv   # show a bottle being inserted

try:
    BASE = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE = os.getcwd()
OUT = os.path.join(BASE, "renders")
os.makedirs(OUT, exist_ok=True)

# Cabinet dimensions (metres). Front of the machine faces -Y.
W = 0.78          # width  (X)
D = 0.80          # depth  (Y)
H = 1.85          # height (Z)
FRONT = -D / 2.0  # y of the front face
DECAL = FRONT - 0.004  # sit decals/text just in front of the surface

# Palette - Keep It Green brand tokens (sRGB 0-1, from brand/tokens.json)
C_SPRING = (0.094, 0.788, 0.392)   # #18C964 primary: mark, accents
C_FOREST = (0.047, 0.231, 0.165)   # #0C3B2A dark machine panels
C_SUN    = (1.000, 0.784, 0.239)   # #FFC83D coins / points
C_MINT   = (0.863, 0.945, 0.886)   # #DCF1E2 tint surface
C_PAPER  = (0.965, 0.969, 0.945)   # #F6F7F1 body shell
C_CHAR   = (0.075, 0.125, 0.102)   # #13201A near-black
C_MUTED  = (0.420, 0.478, 0.447)   # #6B7A72 secondary
C_WHITE  = (0.985, 0.990, 0.985)
C_METAL  = (0.78, 0.80, 0.83)      # brushed metal trim


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
def activate(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def _set(b, name, val):
    inp = b.inputs.get(name)
    if inp is not None:
        inp.default_value = val


def _s2l(c):
    """sRGB channel -> scene-linear (Blender Base Color expects linear)."""
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lin(col):
    return tuple(_s2l(c) for c in col)


def make_mat(name, color, metallic=0.0, roughness=0.5,
             emission=None, e_strength=0.0, alpha=1.0,
             coat=0.0, transmission=0.0, ior=1.45, specular=None):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    b = mat.node_tree.nodes.get("Principled BSDF")
    _set(b, "Base Color", (*lin(color), 1.0))
    _set(b, "Metallic", metallic)
    _set(b, "Roughness", roughness)
    _set(b, "IOR", ior)
    if specular is not None:
        _set(b, "Specular IOR Level", specular)
    if coat:
        _set(b, "Coat Weight", coat)
        _set(b, "Coat Roughness", 0.05)
    if transmission:
        _set(b, "Transmission Weight", transmission)
    if emission is not None:
        _set(b, "Emission Color", (*lin(emission), 1.0))
        _set(b, "Emission Strength", e_strength)
    if alpha < 1.0:
        _set(b, "Alpha", alpha)
        mat.blend_method = "BLEND"
    return mat


def set_mat(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)


def smooth(obj, angle=40):
    activate(obj)
    try:
        bpy.ops.object.shade_auto_smooth(angle=radians(angle))
    except Exception:
        try:
            bpy.ops.object.shade_smooth()
        except Exception:
            pass


def add_box(name, dims, loc, mat=None, bevel=0.0, seg=3):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = (dims[0], dims[1], dims[2])
    activate(o)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel > 0:
        m = o.modifiers.new("bevel", "BEVEL")
        m.width = bevel
        m.segments = seg
        m.limit_method = "ANGLE"
        m.angle_limit = radians(40)
        activate(o)
        bpy.ops.object.modifier_apply(modifier=m.name)
        smooth(o)
    if mat:
        set_mat(o, mat)
    return o


def add_cyl(name, radius, depth, loc, mat=None, axis="Z", verts=48,
            caps="NGON"):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius,
                                        depth=depth, location=loc,
                                        end_fill_type=caps)
    o = bpy.context.active_object
    o.name = name
    if axis == "Y":
        o.rotation_euler = (radians(90), 0, 0)
        activate(o)
        bpy.ops.object.transform_apply(rotation=True)
    smooth(o)
    if mat:
        set_mat(o, mat)
    return o


def add_cone(name, r1, r2, depth, loc, mat=None, axis="Z", verts=32):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2,
                                    depth=depth, location=loc)
    o = bpy.context.active_object
    o.name = name
    if axis == "Y":
        o.rotation_euler = (radians(90), 0, 0)
        activate(o)
        bpy.ops.object.transform_apply(rotation=True)
    smooth(o)
    if mat:
        set_mat(o, mat)
    return o


def boolean_diff(target, cutter):
    activate(target)
    m = target.modifiers.new("cut", "BOOLEAN")
    m.operation = "DIFFERENCE"
    m.object = cutter
    m.solver = "EXACT"
    bpy.ops.object.modifier_apply(modifier=m.name)


def add_torus(name, major, minor, loc, mat=None):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor,
                                     location=loc,
                                     major_segments=64, minor_segments=18)
    o = bpy.context.active_object
    o.name = name
    o.rotation_euler = (radians(90), 0, 0)   # stand the ring up on the front
    activate(o)
    bpy.ops.object.transform_apply(rotation=True)
    smooth(o)
    if mat:
        set_mat(o, mat)
    return o


def add_text(body, size, loc, mat, rot=(radians(90), 0, 0), extrude=0.004,
             align="CENTER"):
    bpy.ops.object.text_add(location=loc)
    t = bpy.context.active_object
    t.data.body = body
    t.data.size = size
    t.data.extrude = extrude
    t.data.align_x = align
    t.data.align_y = "CENTER"
    t.rotation_euler = rot
    activate(t)
    bpy.ops.object.convert(target="MESH")
    set_mat(t, mat)
    return t


def look_at(obj, target):
    d = Vector(target) - obj.location
    obj.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def make_leaf(name, center, size, mat):
    """Pointed leaf via boolean intersection of two discs (fallback: ellipse)."""
    cx, cy, cz = center
    a = b = None
    try:
        bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=size,
                                            depth=0.05, location=(cx - size * 0.55, cy, cz))
        a = bpy.context.active_object
        a.rotation_euler = (radians(90), 0, 0)
        activate(a)
        bpy.ops.object.transform_apply(rotation=True)

        bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=size,
                                            depth=0.05, location=(cx + size * 0.55, cy, cz))
        b = bpy.context.active_object
        b.rotation_euler = (radians(90), 0, 0)
        activate(b)
        bpy.ops.object.transform_apply(rotation=True)

        activate(a)
        m = a.modifiers.new("bool", "BOOLEAN")
        m.operation = "INTERSECT"
        m.object = b
        m.solver = "EXACT"
        bpy.ops.object.modifier_apply(modifier=m.name)
        bpy.data.objects.remove(b, do_unlink=True)
        b = None
        a.name = name
        a.rotation_euler = (0, radians(22), 0)
        set_mat(a, mat)
        leaf = a
    except Exception as e:
        print("leaf boolean failed, using ellipse fallback:", e)
        for o in (a, b):
            try:
                if o:
                    bpy.data.objects.remove(o, do_unlink=True)
            except Exception:
                pass
        bpy.ops.mesh.primitive_uv_sphere_add(radius=size, location=center)
        leaf = bpy.context.active_object
        leaf.name = name
        leaf.scale = (0.6, 0.05, 1.0)
        activate(leaf)
        bpy.ops.object.transform_apply(scale=True)
        leaf.rotation_euler = (0, radians(22), 0)
        smooth(leaf)
        set_mat(leaf, mat)
    return leaf


def make_bottle(cz, mat_glass, mat_cap, mat_label):
    """A translucent PET bottle, horizontal, half-inserted into the intake."""
    x = 0.0
    add_cyl("bottle_body", 0.036, 0.17, (x, -0.30, cz), mat_glass,
            axis="Y", verts=40)
    add_cone("bottle_shoulder", 0.036, 0.015, 0.07, (x, -0.45, cz), mat_glass,
             axis="Y", verts=40)
    add_cyl("bottle_neck", 0.015, 0.05, (x, -0.51, cz), mat_glass,
            axis="Y", verts=24)
    add_cyl("bottle_cap", 0.018, 0.03, (x, -0.55, cz), mat_cap,
            axis="Y", verts=24)
    add_cyl("bottle_label", 0.038, 0.06, (x, -0.28, cz), mat_label,
            axis="Y", verts=40, caps="NOTHING")


def make_token(name, center, size, depth, mat):
    """Rounded-square brand 'token' (radius 28%), facing -Y."""
    return add_box(name, (size, depth, size), center, mat,
                   bevel=0.28 * size, seg=6)


def make_brand_leaf(name, center, height, mat, thickness=0.012):
    """Recreate the exact brand leaf (SVG path) as extruded 3D geometry."""
    s = height / 62.0

    def P(xs, ys):                       # SVG (100x100, y-down) -> local XY
        return Vector(((xs - 50) * s, (50 - ys) * s, 0))

    cu = bpy.data.curves.new(name + "_c", type="CURVE")
    cu.dimensions = "2D"
    cu.resolution_u = 16
    cu.extrude = thickness / 2.0
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(1)
    for bp in sp.bezier_points:
        bp.handle_left_type = bp.handle_right_type = "FREE"
    a, b = sp.bezier_points
    a.co, a.handle_right, a.handle_left = P(50, 20), P(72, 35), P(28, 35)
    b.co, b.handle_left, b.handle_right = P(50, 82), P(72, 63), P(28, 63)
    sp.use_cyclic_u = True

    obj = bpy.data.objects.new(name, cu)
    bpy.context.collection.objects.link(obj)
    activate(obj)
    bpy.ops.object.convert(target="MESH")
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY")
    obj.rotation_euler = (radians(90), 0, 0)   # stand upright, face -Y
    activate(obj)
    bpy.ops.object.transform_apply(rotation=True)
    obj.location = center
    set_mat(obj, mat)
    return obj


# ----------------------------------------------------------------------------
# Build
# ----------------------------------------------------------------------------
def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.curves,
                 bpy.data.lights, bpy.data.cameras):
        for blk in list(coll):
            if blk.users == 0:
                coll.remove(blk)


def build():
    m_body   = make_mat("body",   C_PAPER,  roughness=0.3, coat=0.2)
    m_panel  = make_mat("panel",  C_FOREST, roughness=0.4, coat=0.12)   # matte deep-green panel
    m_char   = make_mat("char",   C_CHAR,   metallic=0.2, roughness=0.45)
    m_muted  = make_mat("muted",  C_MUTED,  roughness=0.5)
    m_spring = make_mat("spring", C_SPRING, roughness=0.4, specular=0.2)
    m_springE= make_mat("springE", C_SPRING, emission=C_SPRING, e_strength=0.9)
    m_mint   = make_mat("mint",   C_MINT,   roughness=0.4)
    m_greenE = make_mat("greenE", C_SPRING, emission=C_SPRING, e_strength=2.4)
    m_ledE   = make_mat("ledE",   C_SPRING, emission=C_SPRING, e_strength=1.9)
    m_screen = make_mat("screen", C_FOREST, roughness=0.1, specular=0.4,
                        emission=C_FOREST, e_strength=0.5)
    m_white  = make_mat("white",  C_WHITE, roughness=0.45,
                        emission=C_WHITE, e_strength=0.75)
    m_sunE   = make_mat("sunE",   C_SUN,   emission=C_SUN, e_strength=2.0)
    m_metal  = make_mat("metal",  C_METAL, metallic=1.0, roughness=0.2)
    m_rubber = make_mat("rubber", C_CHAR,  roughness=0.6)
    m_leafW  = make_mat("leafW",  C_WHITE, emission=C_WHITE, e_strength=1.3)
    m_glass  = make_mat("glass",  (0.80, 0.92, 0.85), roughness=0.04,
                        transmission=1.0, ior=1.45)
    m_cap    = make_mat("cap",    C_SPRING, roughness=0.35)
    m_label  = make_mat("label",  C_PAPER, roughness=0.4)

    # Plinth / base
    add_box("plinth", (W + 0.06, D + 0.06, 0.07), (0, 0, 0.035), m_char, bevel=0.01)
    add_box("base", (W + 0.02, D + 0.02, 0.10), (0, 0, 0.12), m_metal, bevel=0.012)

    # Main cabinet (Paper shell)
    cabinet = add_box("cabinet", (W, D, H - 0.17), (0, 0, 0.17 + (H - 0.17) / 2),
                      m_body, bevel=0.03, seg=4)

    # ---- Deep-Forest control spine (carries the UI) ---------------------
    panel = add_box("control_panel", (0.56, 0.06, 0.98), (0, FRONT, 1.22),
                    m_panel, bevel=0.025, seg=4)
    pf = FRONT - 0.035   # just in front of the panel face
    pd = FRONT - 0.05    # decal plane on the panel

    # ---- Crown / header (Forest panel + leaf-token logo + wordmark) -----
    add_box("crown", (W + 0.015, D + 0.03, 0.17), (0, 0, H - 0.03),
            m_panel, bevel=0.02)
    cf = -(D + 0.03) / 2 - 0.006    # just in front of the crown face
    make_token("logo_token", (-0.27, cf, H - 0.03), 0.12, 0.02, m_springE)
    make_brand_leaf("logo_leaf", (-0.27, cf - 0.014, H - 0.03), 0.086, m_leafW)
    add_text("KEEP IT GREEN", 0.052, (0.08, cf, H - 0.03), m_white)

    # ---- Touchscreen (Forest display, brand UI) -------------------------
    add_box("screen_bezel", (0.50, 0.04, 0.34), (0, pf, 1.50), m_panel, bevel=0.012)
    sb = pf - 0.02
    add_box("screen", (0.45, 0.02, 0.29), (0, sb, 1.50), m_screen)
    sd = sb - 0.012      # on-screen UI plane
    make_token("ui_token", (0, sd, 1.585), 0.075, 0.006, m_springE)
    make_brand_leaf("ui_leaf", (0, sd - 0.006, 1.585), 0.052, m_leafW)
    add_text("KEEP IT GREEN", 0.027, (0, sd, 1.498), m_white)
    add_box("ui_pill", (0.21, 0.006, 0.052), (0, sd + 0.004, 1.428), m_sunE,
            bevel=0.026, seg=6)
    add_text("+15 PTS", 0.028, (0, sd, 1.428), m_char)

    # ---- AI-vision camera module ----------------------------------------
    add_box("cam_housing", (0.22, 0.06, 0.11), (0, pf - 0.01, 1.25), m_panel, bevel=0.014)
    add_cyl("cam_lens", 0.038, 0.06, (0, pf - 0.05, 1.25), m_screen, axis="Y")
    add_torus("cam_ring", 0.048, 0.007, (0, pf - 0.06, 1.25), m_greenE)
    add_text("AI VISION", 0.022, (0, pd, 1.16), m_greenE)

    # ---- Real bored insertion hole + dark chamber -----------------------
    iz = 0.95                                   # intake centre height
    cutter = add_cyl("cutter", 0.12, 0.7, (0, -0.18, iz), None, axis="Y")
    try:
        boolean_diff(cabinet, cutter)
        boolean_diff(panel, cutter)
    except Exception as e:
        print("intake boolean failed:", e)
    bpy.data.objects.remove(cutter, do_unlink=True)
    # dark liner down the bore + back wall (the chamber you see into)
    add_cyl("intake_liner", 0.117, 0.34, (0, -0.27, iz), m_rubber,
            axis="Y", caps="NOTHING")
    add_cyl("intake_back", 0.13, 0.012, (0, 0.07, iz), m_char, axis="Y")
    add_torus("intake_gasket", 0.122, 0.016, (0, pf + 0.005, iz), m_rubber)
    add_torus("intake_ring", 0.142, 0.022, (0, pf - 0.02, iz), m_greenE)
    add_text("INSERT  BOTTLE / CAN", 0.023, (0, pd, 0.78), m_white)
    if BOTTLE:
        make_bottle(iz, m_glass, m_cap, m_label)

    # ---- Coin / receipt tray (Sun-yellow accent) ------------------------
    add_box("tray_slot", (0.26, 0.05, 0.05), (0, FRONT + 0.018, 0.64), m_rubber, bevel=0.008)
    add_box("tray_lip", (0.28, 0.07, 0.014), (0, FRONT - 0.04, 0.61), m_sunE, bevel=0.005)
    add_text("COINS / RECEIPT", 0.019, (0, FRONT - 0.012, 0.565), m_char)

    # ---- Two sorted compartments (Plastic=Spring | Aluminum=Mint) -------
    door_w, door_h, door_cz = 0.345, 0.40, 0.33
    for sign, label, accent, lid in ((-1, "PLASTIC", m_spring, "BOTTLES"),
                                     (1, "ALUMINUM", m_mint, "CANS")):
        x = sign * 0.185
        add_box(f"door_{label}", (door_w, 0.03, door_h), (x, FRONT, door_cz),
                m_body, bevel=0.014)
        df = FRONT - 0.02          # decal plane in front of the door
        add_box(f"stripe_{label}", (door_w, 0.02, 0.08),
                (x, df + 0.006, door_cz + door_h / 2 - 0.055), accent)
        add_text(label, 0.030, (x, df, door_cz + door_h / 2 - 0.055), m_char)
        add_text(lid, 0.019, (x, df, door_cz), m_muted)
        add_box(f"handle_{label}", (0.17, 0.03, 0.02),
                (x, df - 0.005, door_cz - door_h / 2 + 0.07), m_metal, bevel=0.008)

    # ---- Vertical Spring-green LED accent strips ------------------------
    for sx in (-1, 1):
        add_box(f"led_{sx}", (0.018, 0.025, 1.34),
                (sx * (W / 2 - 0.014), FRONT - 0.004, 0.95), m_ledE, bevel=0.005)

    # ---- Side vents (subtle detail) -------------------------------------
    for i in range(5):
        add_box(f"vent_{i}", (0.004, 0.18, 0.012),
                (W / 2 + 0.001, 0.10, 1.28 + i * 0.05), m_char)


# ----------------------------------------------------------------------------
# Stage: floor, world, lights, cameras
# ----------------------------------------------------------------------------
def make_floor():
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "floor"
    set_mat(floor, make_mat("floor", (0.50, 0.52, 0.55), roughness=0.12,
                            coat=0.2))
    return floor


def make_world():
    world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.82, 0.85, 0.89, 1.0)
        bg.inputs[1].default_value = 0.22


def add_area(name, loc, target, energy, size):
    bpy.ops.object.light_add(type="AREA", location=loc)
    light = bpy.context.active_object
    light.name = name
    light.data.energy = energy
    light.data.size = size
    look_at(light, target)
    return light


def make_lights():
    t = (0, 0, 1.0)
    add_area("key",  (-3.0, -3.0, 3.6), t, 1800, 3.5)   # soft key (left)
    add_area("fill", (3.6, -2.4, 2.2), t, 550, 3.5)     # soft fill (right)
    add_area("rim",  (0.6, 3.6, 3.6), t, 1300, 3.0)     # rim / separation
    add_area("top",  (0, -0.4, 5.2), t, 300, 5.0)       # soft top


def make_camera(loc, target, lens):
    bpy.ops.object.camera_add(location=loc)
    cam = bpy.context.active_object
    cam.data.lens = lens
    look_at(cam, target)
    bpy.context.scene.camera = cam
    return cam


# ----------------------------------------------------------------------------
# Render
# ----------------------------------------------------------------------------
def setup_render():
    s = bpy.context.scene
    s.render.engine = "CYCLES"
    try:
        s.view_settings.view_transform = "AgX"
        s.view_settings.look = "AgX - High Contrast"
    except Exception as e:
        print("view transform note:", e)
    try:
        s.cycles.device = "CPU"
        s.cycles.samples = 14 if QUICK else 128
        s.cycles.use_denoising = True
        try:
            s.cycles.denoiser = "OPENIMAGEDENOISE"
        except Exception:
            pass
    except Exception as e:
        print("cycles config note:", e)
    s.render.resolution_x = 900 if QUICK else 1500
    s.render.resolution_y = 1125 if QUICK else 1875
    s.render.resolution_percentage = 100
    s.render.image_settings.file_format = "PNG"
    s.render.image_settings.color_mode = "RGBA"


def render_shot(name, cam_loc, target, lens, floor, transparent=False,
                show_bottle=True):
    s = bpy.context.scene
    make_camera(cam_loc, target, lens)
    s.render.film_transparent = transparent
    floor.is_shadow_catcher = transparent
    floor.hide_render = False
    for o in bpy.data.objects:
        if o.name.startswith("bottle_"):
            o.hide_render = not show_bottle
    s.render.filepath = os.path.join(OUT, name)
    print(f"  rendering {name} ...")
    bpy.ops.render.render(write_still=True)


def export_models():
    """Export the machine (meshes only, no floor/lights/camera) for reuse."""
    bpy.ops.object.select_all(action="DESELECT")
    sel = []
    for o in bpy.data.objects:
        if o.type == "MESH" and o.name != "floor":
            o.select_set(True)
            sel.append(o)
    if not sel:
        return
    bpy.context.view_layer.objects.active = sel[0]

    glb = os.path.join(BASE, "keep_it_green_machine.glb")
    bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB",
                              use_selection=True)
    print("Exported:", glb)
    try:
        fbx = os.path.join(BASE, "keep_it_green_machine.fbx")
        bpy.ops.export_scene.fbx(filepath=fbx, use_selection=True)
        print("Exported:", fbx)
    except Exception as e:
        print("fbx export note:", e)
    try:
        obj = os.path.join(BASE, "keep_it_green_machine.obj")
        bpy.ops.wm.obj_export(filepath=obj, export_selected_objects=True)
        print("Exported:", obj)
    except Exception as e:
        print("obj export note:", e)


def main():
    clear_scene()
    build()
    floor = make_floor()
    make_world()
    make_lights()
    setup_render()

    render_shot("keep_it_green_front.png", (0, -3.9, 1.05), (0, 0, 1.0),
                72, floor, show_bottle=False)
    render_shot("keep_it_green_hero.png", (2.5, -3.1, 1.45), (0, 0, 0.95),
                62, floor)
    render_shot("keep_it_green_cutout.png", (2.1, -3.3, 1.30), (0, 0, 0.95),
                62, floor, transparent=True)

    blend = os.path.join(BASE, "keep_it_green_machine.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend)
    print("Saved:", blend)
    export_models()
    print("Renders in:", OUT)


if __name__ == "__main__":
    main()
