# Cleanly redraw the ER diagram (Figure 4.3) with correctly-sized boxes and orthogonal connectors.
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
import os

OUT = os.path.join(os.path.dirname(__file__), "assets", "diagrams")
FOREST="#0C3B2A"; GREEN="#1B7A3D"; PAPER="#FFFFFF"; INK="#1A1A1A"; LINE="#5A5A5A"; GREY="#6B6B6B"
plt.rcParams["font.family"]="DejaVu Sans"

fig, ax = plt.subplots(figsize=(11, 8.4), dpi=150)
ax.set_xlim(0,100); ax.set_ylim(0,100); ax.axis("off")
ax.text(50, 98.5, "Entity–Relationship Model (simplified)", ha="center", fontsize=15, weight="bold", color=FOREST)

HH=6.5; RH=4.0; PAD=2.0
def entity(x, top, w, title, fields):
    h = HH + len(fields)*RH + PAD
    bottom = top - h
    ax.add_patch(Rectangle((x, bottom), w, h, facecolor=PAPER, edgecolor=GREEN, lw=1.8, zorder=4))
    ax.add_patch(Rectangle((x, top-HH), w, HH, facecolor=GREEN, edgecolor=GREEN, zorder=5))
    ax.text(x+w/2, top-HH/2, title, ha="center", va="center", color="white", fontsize=10.5, weight="bold", zorder=6)
    for i,f in enumerate(fields):
        fy = top - HH - PAD*0.4 - RH*(i+0.5)
        pk = "(PK)" in f
        ax.text(x+2.2, fy, f, ha="left", va="center", fontsize=8.4, color=INK,
                weight="bold" if pk else "normal", zorder=6)
    return dict(x=x, top=top, w=w, h=h, bottom=bottom, cx=x+w/2, right=x+w)

def poly(pts, color=LINE, lw=1.6):
    for i in range(len(pts)-1):
        ax.add_line(Line2D([pts[i][0],pts[i+1][0]],[pts[i][1],pts[i+1][1]], color=color, lw=lw, zorder=2))
    for p in (pts[0], pts[-1]):
        ax.add_patch(plt.Circle(p, 0.7, color=color, zorder=3))
def card(x, y, t):
    ax.text(x, y, t, ha="center", va="center", fontsize=9, color=FOREST, weight="bold", zorder=7,
            bbox=dict(boxstyle="circle,pad=0.12", fc="white", ec="none"))

# Entities
U  = entity(6,  91, 26, "User",         ["Id (PK)","Email","Points","Role"])
M  = entity(68, 91, 26, "Machine",      ["Id (PK)","Name","Location","IsAvailable"])
O  = entity(6,  60, 30, "Otp / Session",["Id (PK)","Code","UserId (FK)","MachineId (FK)","Status"])
T  = entity(64, 60, 30, "Transaction",  ["Id (PK)","UserId (FK)","MachineId (FK)","ItemType","Points"])
V  = entity(4,  27, 20, "Vendor",       ["Id (PK)","Name"])
Pr = entity(38, 27, 24, "Promo",        ["Id (PK)","VendorId (FK)","Code","Cost"])
Rd = entity(70, 27, 26, "Redemption",   ["Id (PK)","UserId (FK)","PromoId (FK)"])

# Relationships (1 : many)
# User -> Otp
poly([(18, U["bottom"]), (18, O["top"])]); card(18, U["bottom"]-1.6, "1"); card(18, O["top"]+1.8, "N")
# Machine -> Transaction
poly([(82, M["bottom"]), (82, T["top"])]); card(82, M["bottom"]-1.6, "1"); card(82, T["top"]+1.8, "N")
# Machine -> Otp  (channel at y=64.7)
poly([(70, M["bottom"]), (70, 64.7), (31, 64.7), (31, O["top"])]); card(70, M["bottom"]-1.6, "1"); card(31, O["top"]+1.8, "N")
# User -> Transaction (channel at y=66.7, parallel, no crossing)
poly([(30, U["bottom"]), (30, 66.7), (70, 66.7), (70, T["top"])]); card(30, U["bottom"]-1.6, "1"); card(70, T["top"]+1.8, "N")
# Vendor -> Promo
poly([(V["right"], 18.5), (Pr["x"], 18.5)]); card(V["right"]+1.6, 18.5, "1"); card(Pr["x"]-1.6, 18.5, "N")
# Promo -> Redemption
poly([(Pr["right"], 18.0), (Rd["x"], 18.0)]); card(Pr["right"]+1.6, 18.0, "1"); card(Rd["x"]-1.6, 18.0, "N")
# User -> Redemption (border route, bottom channel y=1.8)
poly([(6, 80), (2, 80), (2, 1.8), (86, 1.8), (86, Rd["bottom"])]); card(4.0, 78, "1"); card(86, Rd["bottom"]-1.6, "N")

ax.text(50, 95, "1 : N relationships;  FK = foreign key,  PK = primary key", ha="center", fontsize=9.5, color=GREY, style="italic")
fig.savefig(os.path.join(OUT, "er.png"), bbox_inches="tight", pad_inches=0.15, facecolor=PAPER)
print("wrote er.png (fixed)")
