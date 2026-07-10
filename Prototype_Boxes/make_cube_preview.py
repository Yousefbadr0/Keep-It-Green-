"""Assembled preview of the servo-lid cube: open-top finger-jointed box + the
hinged lid shown OPEN, driven by the SG90 on the right wall. Renders per box."""
import bpy, json, os, sys
from math import radians
from mathutils import Vector

BASE = os.path.dirname(os.path.abspath(__file__))
L, T = 100.0, 3.0
HB, HZ = 17.0, 80.0
LABEL = "ALUMINUM" if "alu" in sys.argv else "PLASTIC"
BODY = (0.863, 0.945, 0.886) if LABEL == "ALUMINUM" else (0.094, 0.788, 0.392)


def s2l(c): return c/12.92 if c <= 0.04045 else ((c+0.055)/1.055)**2.4
def lin(c): return tuple(s2l(x) for x in c)


panels = json.load(open(os.path.join(BASE, "out", f"keepitgreen_cube_{LABEL}_panels.json")))
bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.delete()

M = {"BOTTOM": lambda u, v, t: (u, v, t), "FRONT": lambda u, v, t: (u, t, v),
     "BACK": lambda u, v, t: (u, L-T+t, v), "LEFT": lambda u, v, t: (t, u, v),
     "RIGHT": lambda u, v, t: (L-T+t, u, v)}


def kkey(name):
    for k in M:
        if name.startswith(k):
            return k
    return None


def dedupe(pts):
    out = []
    for p in pts:
        if not out or abs(out[-1][0]-p[0]) > 1e-6 or abs(out[-1][1]-p[1]) > 1e-6:
            out.append(tuple(p))
    if len(out) > 1 and out[0] == out[-1]:
        out.pop()
    return out


def mat(name, col, rough=0.45, metallic=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*lin(col), 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metallic
    return m


def activate(o):
    bpy.ops.object.select_all(action="DESELECT"); o.select_set(True)
    bpy.context.view_layer.objects.active = o


def cut(target, cutter):
    activate(target)
    md = target.modifiers.new("b", "BOOLEAN"); md.operation = "DIFFERENCE"
    md.object = cutter; md.solver = "EXACT"
    bpy.ops.object.modifier_apply(modifier=md.name)
    bpy.data.objects.remove(cutter, do_unlink=True)


def prism(name, outline, m, mtl):
    out = dedupe(outline); n = len(out)
    verts = [m(u, v, 0) for (u, v) in out] + [m(u, v, T) for (u, v) in out]
    faces = [list(range(n)), list(range(2*n-1, n-1, -1))]
    for i in range(n):
        j = (i+1) % n
        faces.append([i, j, n+j, n+i])
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    ob = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mtl); return ob


m_body = mat("body", BODY)
m_dark = mat("dark", (0.047, 0.231, 0.165))
m_servo = mat("servo", (0.10, 0.22, 0.62))
m_metal = mat("metal", (0.8, 0.82, 0.85), rough=0.3, metallic=1.0)

# --- box: bottom + 4 walls ---
for p in panels:
    k = kkey(p["name"])
    if k is None:
        continue
    ob = prism(k, p["outline"], M[k], m_body)
    if k == "RIGHT":          # servo window + screw/wire holes
        bpy.ops.mesh.primitive_cube_add(size=1, location=(L-1.5, L-HB, HZ))
        c = bpy.context.active_object; c.scale = (3*T, 12.6, 23.2)
        activate(c); bpy.ops.object.transform_apply(scale=True); cut(ob, c)
    if k == "BACK":           # cable hole
        bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=3.5, depth=4*T,
                                            location=(50, L-1.5, 18),
                                            rotation=(radians(90), 0, 0))
        cut(ob, bpy.context.active_object)

# --- engraved branding on the front wall ---
for s, size, zz in ((LABEL, 13, 46), ("KEEP IT GREEN", 5, 62)):
    bpy.ops.object.text_add()
    tt = bpy.context.active_object
    tt.data.body = s; tt.data.size = size
    tt.data.align_x = "CENTER"; tt.data.align_y = "CENTER"; tt.data.extrude = 0.3
    tt.rotation_euler = (radians(90), 0, 0); tt.location = (50, -0.3, zz)
    activate(tt); bpy.ops.object.convert(target="MESH")
    tt.data.materials.append(m_dark)

# --- servo body through the right wall + horn ---
bpy.ops.mesh.primitive_cube_add(size=1, location=(L-T-11, L-HB, HZ))
sv = bpy.context.active_object; sv.scale = (22, 12, 22.5)
activate(sv); bpy.ops.object.transform_apply(scale=True)
sv.data.materials.append(m_servo); sv.name = "servo"

# --- lid (built flat, then rotated OPEN about the back-top edge) ---
lidp = next(p for p in panels if p["name"] == "LID")
out = dedupe(lidp["outline"]); n = len(out)
verts = [(x, y-L, (L)-L) for (x, y) in out] + [(x, y-L, (L+T)-L) for (x, y) in out]
faces = [list(range(n)), list(range(2*n-1, n-1, -1))]
for i in range(n):
    j = (i+1) % n
    faces.append([i, j, n+j, n+i])
me = bpy.data.meshes.new("LID"); me.from_pydata(verts, [], faces); me.update()
lid = bpy.data.objects.new("LID", me); bpy.context.collection.objects.link(lid)
lid.data.materials.append(m_body)
lid.location = (0, L, L)
lid.rotation_euler = (radians(-66), 0, 0)       # cover swung open
# grip notch
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=11, depth=20, location=(50, 12, L+T/2))
gc = bpy.context.active_object
gc.parent = lid; gc.matrix_parent_inverse = lid.matrix_world.inverted()
cut(lid, gc)
# label engraved on the lid
bpy.ops.object.text_add()
t = bpy.context.active_object
t.data.body = LABEL; t.data.size = 11; t.data.align_x = "CENTER"; t.data.align_y = "CENTER"
t.data.extrude = 0.4
activate(t); bpy.ops.object.convert(target="MESH")
t.location = (50, 55, L + T)
t.parent = lid; t.matrix_parent_inverse = lid.matrix_world.inverted()
t.data.materials.append(m_dark)

# --- two hinge brackets under the lid back (ride the pivots) ---
for bxp in (14, L-14):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(bxp, L-6, HZ+6))
    br = bpy.context.active_object; br.scale = (5, 4, 20)
    activate(br); bpy.ops.object.transform_apply(scale=True)
    br.data.materials.append(m_dark)

# --- stage ---
bpy.ops.mesh.primitive_plane_add(size=2000, location=(50, 50, 0))
bpy.context.active_object.data.materials.append(mat("floor", (0.6, 0.62, 0.64), rough=0.2))


def look_at(o, tgt):
    o.rotation_euler = (Vector(tgt)-o.location).to_track_quat("-Z", "Y").to_euler()


bpy.ops.object.camera_add(location=(250, -235, 205))
cam = bpy.context.active_object; cam.data.lens = 55
look_at(cam, (48, 50, 55)); bpy.context.scene.camera = cam
for loc, e in (((-140, -200, 260), 4.0), ((260, -120, 150), 1.7), ((60, 260, 240), 2.3)):
    bpy.ops.object.light_add(type="SUN", location=loc)
    li = bpy.context.active_object; li.data.energy = e; li.data.angle = radians(6)
    look_at(li, (50, 50, 55))

sc = bpy.context.scene
w = bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True
bg = w.node_tree.nodes["Background"]
bg.inputs[0].default_value = (*lin((0.82, 0.85, 0.89)), 1); bg.inputs[1].default_value = 0.5
sc.render.engine = "CYCLES"; sc.cycles.samples = 110; sc.cycles.use_denoising = True
sc.view_settings.view_transform = "AgX"
try: sc.view_settings.look = "AgX - High Contrast"
except Exception: pass
sc.render.resolution_x = 1500; sc.render.resolution_y = 1200
sc.render.filepath = os.path.join(BASE, "renders", f"cube_{LABEL}.png")
bpy.ops.render.render(write_still=True)
print("preview done", LABEL)
