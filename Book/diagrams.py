# Generate branded system diagrams for the Keep It Green graduation book.
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from matplotlib.lines import Line2D
import os

OUT = os.path.join(os.path.dirname(__file__), "assets", "diagrams")
os.makedirs(OUT, exist_ok=True)

FOREST = "#0C3B2A"; GREEN = "#1B7A3D"; SPRING = "#18C964"; SUN = "#F5B301"
PAPER = "#FFFFFF"; INK = "#1A1A1A"; MIST = "#E8F3EC"; LINE = "#4A4A4A"; GREY = "#6B6B6B"
plt.rcParams["font.family"] = "DejaVu Sans"

def box(ax, x, y, w, h, text, fc=MIST, ec=GREEN, tc=INK, fs=10, bold=True, r=0.02, lw=1.6):
    p = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.01,rounding_size={r}",
                       linewidth=lw, edgecolor=ec, facecolor=fc, mutation_aspect=1)
    ax.add_patch(p)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            color=tc, weight="bold" if bold else "normal", wrap=True, zorder=5)

def arrow(ax, p1, p2, color=LINE, style="-|>", lw=1.6, ls="-", rad=0.0):
    a = FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=14, color=color,
                        lw=lw, linestyle=ls, connectionstyle=f"arc3,rad={rad}", zorder=3)
    ax.add_patch(a)

def newfig(w=11, h=7):
    fig, ax = plt.subplots(figsize=(w, h), dpi=150)
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")
    return fig, ax

def save(fig, name):
    fig.savefig(os.path.join(OUT, name), bbox_inches="tight", pad_inches=0.15, facecolor=PAPER)
    plt.close(fig)
    print("wrote", name)

# ---------- 1. SYSTEM ARCHITECTURE ----------
fig, ax = newfig(11, 7.2)
ax.text(50, 96, "Keep It Green — System Architecture", ha="center", fontsize=14, weight="bold", color=FOREST)
# clients
box(ax, 4, 74, 26, 12, "AI Machine\n(Python · YOLOv8 · Arduino)", fc="#FFF3D6", ec=SUN)
box(ax, 37, 74, 26, 12, "Mobile App\n(Flutter / Dart)", fc=MIST)
box(ax, 70, 74, 26, 12, "Web App + Kiosk\n(JavaScript PWA)", fc=MIST)
# backend
box(ax, 18, 40, 64, 22, "", fc="#DCF1E2", ec=GREEN)
ax.text(50, 58.5, "Backend REST API  (ASP.NET Core · .NET 10)", ha="center", fontsize=11.5, weight="bold", color=INK)
ax.text(50, 54, "Controllers  →  Services  →  Repositories", ha="center", fontsize=9.5, color=GREY)
box(ax, 23, 43.5, 24, 5.2, "JWT Auth · Roles", fc=PAPER, ec=GREEN, fs=8.5)
box(ax, 53, 43.5, 24, 5.2, "X-Machine-Key", fc=PAPER, ec=SUN, fs=8.5)
# db
box(ax, 32, 14, 36, 12, "SQL Server Database\n(Entity Framework Core)", fc=FOREST, ec=FOREST, tc="white", fs=11)
# arrows clients->api
for cx in (17, 50, 83):
    arrow(ax, (cx, 74), (cx, 62.3), color=LINE)
ax.text(51.5, 68, "HTTPS / REST + JSON", ha="left", fontsize=8.5, color=GREY, style="italic")
# api->db
arrow(ax, (49, 40), (49, 26.2), color=GREEN, lw=2)
arrow(ax, (51, 26.2), (51, 40), color=GREEN, lw=2)
ax.text(53, 33, "EF Core", ha="left", fontsize=8.5, color=GREY, style="italic")
ax.text(50, 8, "Design principle: no client ever touches the database directly — every request is authenticated at the API.",
        ha="center", fontsize=9, color=GREEN, style="italic")
save(fig, "arch.png")

# ---------- 2. RECYCLING SESSION SEQUENCE ----------
fig, ax = newfig(11, 8)
ax.text(50, 97, "Recycling Session — Sequence", ha="center", fontsize=14, weight="bold", color=FOREST)
lanes = [("User", 10), ("Mobile App", 32), ("Machine", 55), ("Backend", 80)]
for name, x in lanes:
    box(ax, x - 9, 88, 18, 6, name, fc="#DCF1E2", ec=GREEN, fs=10)
    ax.add_line(Line2D([x, x], [10, 88], color="#BBBBBB", ls=(0, (4, 3)), lw=1))
def msg(y, x1, x2, text, up=False, color=LINE):
    arrow(ax, (x1, y), (x2, y), color=color)
    ax.text((x1 + x2) / 2, y + 1.2, text, ha="center", fontsize=8.2, color=INK)
X = {n: x for n, x in lanes}
msg(82, X["User"], X["Machine"], "1. Approach / tap Start")
msg(76, X["Machine"], X["Backend"], "2. session/start")
msg(70, X["Backend"], X["Machine"], "3. unique 6-digit code + QR", color=GREEN)
msg(64, X["User"], X["Mobile App"], "4. open app, Scan")
msg(58, X["Mobile App"], X["Backend"], "5. Pair(code)")
msg(52, X["Backend"], X["Mobile App"], "6. paired ✓ (code → user)", color=GREEN)
msg(45, X["User"], X["Machine"], "7. insert item")
msg(39, X["Machine"], X["Machine"], "8. YOLO detect + confirm (≥0.65)")
ax.text(X["Machine"] + 10, 39, "sort via Arduino", ha="left", fontsize=7.6, color=GREY, style="italic")
msg(33, X["Machine"], X["Backend"], "9. submit detection (+ key)")
msg(27, X["Backend"], X["Mobile App"], "10. points update (live)", color=GREEN)
ax.text((X["User"] + X["Machine"]) / 2, 21.5, "steps 7–10 repeat per item", ha="center", fontsize=8, color=SUN, weight="bold")
msg(17, X["User"], X["Mobile App"], "11. tap Finish")
msg(12, X["Mobile App"], X["Backend"], "12. EndSession → machine idles", color=GREEN)
save(fig, "sequence.png")

# ---------- 3. ER DIAGRAM ----------
fig, ax = newfig(11, 7.4)
ax.text(50, 97, "Entity–Relationship Model (simplified)", ha="center", fontsize=14, weight="bold", color=FOREST)
def entity(x, y, title, fields, w=22):
    h = 6 + len(fields) * 3.4
    box(ax, x, y - h, w, h, "", fc=PAPER, ec=GREEN, r=0.01)
    ax.add_patch(Rectangle((x, y - 6), w, 6, facecolor=GREEN, edgecolor=GREEN))
    ax.text(x + w / 2, y - 3, title, ha="center", va="center", color="white", fontsize=10, weight="bold")
    for i, f in enumerate(fields):
        ax.text(x + 1.5, y - 8.6 - i * 3.4, f, ha="left", va="center", fontsize=8, color=INK)
    return (x, y, w, h)
entity(6, 92, "User", ["PK Id", "Email", "Points", "Role"])
entity(39, 92, "Machine", ["PK Id", "Name", "Location", "IsAvailable"])
entity(72, 92, "Otp / Session", ["PK Id", "Code", "FK UserId", "FK MachineId", "Status", "ExpiresAt"])
entity(39, 52, "Transaction", ["PK Id", "FK UserId", "FK MachineId", "ItemType", "Points", "CreatedAt"])
entity(6, 44, "Vendor", ["PK Id", "Name"])
entity(39, 20, "Promo", ["PK Id", "FK VendorId", "Code", "Cost"])
entity(72, 44, "Redemption", ["PK Id", "FK UserId", "FK PromoId", "CreatedAt"])
def rel(p1, p2, rad=0.0):
    arrow(ax, p1, p2, color=LINE, style="-", lw=1.4, rad=rad)
rel((28, 84), (72, 84))          # user-otp (via)
rel((61, 84), (50, 78))          # otp-machine
rel((17, 78), (45, 66))          # user-transaction
rel((50, 74), (50, 66))          # machine-transaction
rel((17, 38), (39, 30), 0.1)     # vendor-promo
rel((28, 74), (78, 58))          # user-redemption
rel((61, 20), (78, 38), -0.2)    # promo-redemption
ax.text(50, 6, "Relationships enforced by EF Core migrations (foreign keys, indexes).", ha="center", fontsize=9, color=GREY, style="italic")
save(fig, "er.png")

# ---------- 4. DEPLOYMENT TOPOLOGY ----------
fig, ax = newfig(11, 6.6)
ax.text(50, 95, "Deployment Topology", ha="center", fontsize=14, weight="bold", color=FOREST)
box(ax, 4, 60, 20, 14, "User Devices\nPhone (APK) ·\nBrowser", fc=MIST)
box(ax, 4, 30, 20, 14, "Recycling\nMachine\n(laptop + cam\n+ Arduino)", fc="#FFF3D6", ec=SUN)
# cloud
box(ax, 36, 20, 60, 62, "", fc="#F3FAF5", ec=GREEN, r=0.02)
ax.text(66, 78, "MonsterASP.NET Cloud (IIS)", ha="center", fontsize=11, weight="bold", color=GREEN)
box(ax, 42, 58, 22, 12, "HTTPS Reverse\nProxy (TLS)", fc=PAPER, ec=GREEN)
box(ax, 70, 58, 22, 12, "ASP.NET App\n(Kestrel)", fc="#DCF1E2", ec=GREEN)
box(ax, 56, 30, 24, 12, "SQL Server DB\n(private network)", fc=FOREST, ec=FOREST, tc="white")
arrow(ax, (24, 67), (42, 64), color=GREEN, lw=1.8)
arrow(ax, (24, 37), (42, 62), color=SUN, lw=1.8)
ax.text(30, 70, "HTTPS", fontsize=8, color=GREY, style="italic")
arrow(ax, (64, 64), (70, 64), color=GREEN)
arrow(ax, (81, 58), (72, 42), color=GREEN)
ax.text(83, 50, "EF Core", fontsize=8, color=GREY, style="italic", rotation=90)
ax.text(66, 24, "Web app + kiosk are served as static files by the same app.", ha="center", fontsize=8.5, color=GREY, style="italic")
save(fig, "deploy.png")

# ---------- 5. USE-CASE DIAGRAM ----------
fig, ax = newfig(11, 7.2)
ax.text(50, 97, "Use-Case Diagram", ha="center", fontsize=14, weight="bold", color=FOREST)
def actor(x, y, name):
    ax.add_patch(plt.Circle((x, y + 7), 2.2, fill=False, ec=INK, lw=1.6))
    ax.add_line(Line2D([x, x], [y + 5, y - 1], color=INK, lw=1.6))
    ax.add_line(Line2D([x - 3, x + 3], [y + 2.5, y + 2.5], color=INK, lw=1.6))
    ax.add_line(Line2D([x, x - 2.6], [y - 1, y - 5], color=INK, lw=1.6))
    ax.add_line(Line2D([x, x + 2.6], [y - 1, y - 5], color=INK, lw=1.6))
    ax.text(x, y - 8, name, ha="center", fontsize=9.5, weight="bold", color=INK)
def uc(x, y, text, fc=MIST):
    e = plt.matplotlib.patches.Ellipse((x, y), 26, 8, facecolor=fc, edgecolor=GREEN, lw=1.4)
    ax.add_patch(e); ax.text(x, y, text, ha="center", va="center", fontsize=8.5, color=INK)
actor(8, 55, "User"); actor(92, 55, "Admin")
box(ax, 26, 8, 48, 82, "", fc="none", ec="#CCCCCC")
ax.text(50, 86, "Keep It Green System", ha="center", fontsize=10, color=GREY, style="italic")
ucs_u = [(40, 78, "Register / Login"), (40, 66, "Pair with machine"), (40, 54, "Recycle item / earn points"),
         (40, 42, "Redeem reward"), (40, 30, "View history")]
for x, y, t in ucs_u:
    uc(x, y, t); arrow(ax, (11, 54), (x - 13, y), color=LINE, style="-", lw=1.2)
ucs_a = [(60, 78, "Manage machines"), (60, 66, "Manage vendors / promos"), (60, 54, "View reports")]
for x, y, t in ucs_a:
    uc(x, y, t, fc="#FFF3D6"); arrow(ax, (89, 54), (x + 13, y), color=LINE, style="-", lw=1.2)
save(fig, "usecase.png")

# ---------- 6. BACKEND LAYERS ----------
fig, ax = newfig(9.5, 6.6)
ax.text(50, 95, "Backend Layered Architecture", ha="center", fontsize=14, weight="bold", color=FOREST)
layers = [("Controllers  (HTTP endpoints, DTOs, auth attributes)", "#DCF1E2"),
          ("Services  (business logic: sessions, points, rewards)", "#E8F3EC"),
          ("Repositories  (data access behind interfaces)", "#EFF7F1"),
          ("DbContext + Entities  (Entity Framework Core)", "#F5FBF7")]
y = 72
for i, (t, c) in enumerate(layers):
    box(ax, 14, y, 72, 12, t, fc=c, ec=GREEN, fs=10)
    if i < 3:
        arrow(ax, (50, y), (50, y - 4.2), color=LINE)
        arrow(ax, (56, y - 4.2), (56, y), color="#AAAAAA", ls="--")
    y -= 16
box(ax, 30, 2, 40, 8, "SQL Server", fc=FOREST, ec=FOREST, tc="white")
arrow(ax, (50, 24), (50, 10.2), color=GREEN)
save(fig, "layers.png")

print("ALL DIAGRAMS DONE")
