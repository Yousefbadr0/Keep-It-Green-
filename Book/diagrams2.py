# Additional diagrams for the Keep It Green book.
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from matplotlib.lines import Line2D
import os

OUT = os.path.join(os.path.dirname(__file__), "assets", "diagrams")
os.makedirs(OUT, exist_ok=True)
FOREST="#0C3B2A"; GREEN="#1B7A3D"; SPRING="#18C964"; SUN="#F5B301"
PAPER="#FFFFFF"; INK="#1A1A1A"; MIST="#E8F3EC"; LINE="#4A4A4A"; GREY="#6B6B6B"
plt.rcParams["font.family"]="DejaVu Sans"

def box(ax,x,y,w,h,text,fc=MIST,ec=GREEN,tc=INK,fs=9.5,bold=True,r=0.02,lw=1.6):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle=f"round,pad=0.01,rounding_size={r}",lw=lw,edgecolor=ec,facecolor=fc))
    ax.text(x+w/2,y+h/2,text,ha="center",va="center",fontsize=fs,color=tc,weight="bold" if bold else "normal",zorder=5)
def arrow(ax,p1,p2,color=LINE,style="-|>",lw=1.6,ls="-",rad=0.0):
    ax.add_patch(FancyArrowPatch(p1,p2,arrowstyle=style,mutation_scale=13,color=color,lw=lw,linestyle=ls,connectionstyle=f"arc3,rad={rad}",zorder=3))
def newfig(w=11,h=6):
    fig,ax=plt.subplots(figsize=(w,h),dpi=150); ax.set_xlim(0,100); ax.set_ylim(0,100); ax.axis("off"); return fig,ax
def save(fig,name):
    fig.savefig(os.path.join(OUT,name),bbox_inches="tight",pad_inches=0.15,facecolor=PAPER); plt.close(fig); print("wrote",name)

# 1. DATA PIPELINE
fig,ax=newfig(11,5.2)
ax.text(50,94,"Dataset Unification Pipeline",ha="center",fontsize=14,weight="bold",color=FOREST)
stages=[("4 public\ndatasets","#FFF3D6",SUN),("Parse &\nconvert labels",MIST,GREEN),("Keep only\n2 classes",MIST,GREEN),
        ("Unify\nformat","#DCF1E2",GREEN),("Split\n3220/483/410",MIST,GREEN),("Augment &\ntrain","#DCF1E2",GREEN)]
x=2; w=13.5; gap=2.7
for i,(t,fc,ec) in enumerate(stages):
    box(ax,x,42,w,20,t,fc=fc,ec=ec,fs=9)
    if i<len(stages)-1: arrow(ax,(x+w,52),(x+w+gap,52),color=GREEN,lw=1.8)
    x+=w+gap
ax.text(50,30,"4,113 images · 4,644 boxes (2,739 plastic / 1,905 aluminium) · full-frame + tight boxes",ha="center",fontsize=9,color=GREY,style="italic")
save(fig,"data_pipeline.png")

# 2. KIOSK STATE MACHINE
fig,ax=newfig(10.5,6)
ax.text(50,95,"Kiosk State Machine",ha="center",fontsize=14,weight="bold",color=FOREST)
box(ax,38,78,24,12,"IDLE\n(show code + QR)",fc="#DCF1E2")
box(ax,38,56,24,12,"PLACE ITEM\n(live camera)",fc=MIST)
box(ax,38,34,24,12,"CONFIRMED\n(+points)",fc=MIST)
box(ax,8,34,22,12,"ASK:\nadd another?",fc="#FFF3D6",ec=SUN)
box(ax,38,12,24,12,"SUMMARY\n(new balance)",fc="#DCF1E2")
arrow(ax,(50,78),(50,68),color=GREEN); ax.text(51,73,"phone pairs",fontsize=7.5,color=GREY)
arrow(ax,(50,56),(50,46),color=GREEN); ax.text(51,51,"item accepted",fontsize=7.5,color=GREY)
arrow(ax,(38,40),(30,40),color=GREEN)
arrow(ax,(19,46),(44,56),color=SUN,rad=-0.3); ax.text(20,54,"another",fontsize=7.5,color=GREY)
arrow(ax,(50,34),(50,24),color=GREEN); ax.text(51,29,"finish",fontsize=7.5,color=GREY)
arrow(ax,(62,18),(75,18),color=GREEN); arrow(ax,(75,18),(75,84),color=GREEN,rad=0); arrow(ax,(75,84),(62,84),color=GREEN)
ax.text(77,50,"session ends → idle",fontsize=7.5,color=GREY,rotation=90,va="center")
save(fig,"kiosk_states.png")

# 3. LOGIN / JWT SEQUENCE
fig,ax=newfig(10.5,5.4)
ax.text(50,94,"Authentication (JWT) Flow",ha="center",fontsize=14,weight="bold",color=FOREST)
for name,x in [("Client",25),("Backend",72)]:
    box(ax,x-13,80,26,8,name,fc="#DCF1E2",ec=GREEN,fs=10)
    ax.add_line(Line2D([x,x],[14,80],color="#BBBBBB",ls=(0,(4,3)),lw=1))
def msg(y,x1,x2,t,color=LINE):
    arrow(ax,(x1,y),(x2,y),color=color); ax.text((x1+x2)/2,y+1.4,t,ha="center",fontsize=8.4,color=INK)
msg(70,25,72,"1. POST /Login  {email, password}")
ax.text(72,62,"2. verify hash, build claims",ha="left",fontsize=8,color=GREY,style="italic")
msg(56,72,25,"3. signed JWT (id, role, expiry)",color=GREEN)
ax.text(25,48,"4. store token",ha="left",fontsize=8,color=GREY,style="italic")
msg(42,25,72,"5. GET /resource  (Authorization: Bearer)")
ax.text(72,34,"6. validate signature + role",ha="left",fontsize=8,color=GREY,style="italic")
msg(28,72,25,"7. 200 OK  /  401  /  403",color=GREEN)
save(fig,"login_sequence.png")

# 4. CLASS / LAYER DIAGRAM
fig,ax=newfig(10.5,6)
ax.text(50,95,"Backend Classes by Layer",ha="center",fontsize=14,weight="bold",color=FOREST)
cols=[("Controllers",8,"UserController\nOtpController\nDetectionController\nMachineController"),
      ("Services",32,"OtpServices\nDetectionServices\nRewardServices\nTokenService"),
      ("Repositories",56,"IUserRepo\nIOtpRepo\nITxnRepo\n(+ EF impl.)"),
      ("Data / Entities",80,"AppDbContext\nUser · Machine\nOtp · Transaction\nVendor · Promo")]
for title,x,body in cols:
    box(ax,x,70,18,14,title,fc="#DCF1E2",ec=GREEN,fs=10)
    box(ax,x,30,18,34,body,fc=PAPER,ec=GREEN,fs=8,bold=False)
    ax.add_patch(Rectangle((x,60),18,4,facecolor=MIST,edgecolor=GREEN))
for x in (26,50,74):
    arrow(ax,(x,47),(x+6,47),color=LINE)
ax.text(50,18,"Each layer depends only on the layer to its right; dependencies are injected.",ha="center",fontsize=9,color=GREY,style="italic")
save(fig,"class_diagram.png")

# 5. GANTT / TIMELINE
fig,ax=newfig(10.5,5)
ax.text(50,94,"Project Timeline (indicative)",ha="center",fontsize=14,weight="bold",color=FOREST)
phases=[("Foundations (backend)",5,26,"#1B7A3D"),
        ("Intelligence (AI model)",22,30,"#2E9E52"),
        ("Clients (mobile/web/kiosk)",40,30,"#18C964"),
        ("Hardware integration",58,20,"#F5B301"),
        ("Hardening & deployment",72,22,"#0C3B2A")]
y=72
for name,x0,w,c in phases:
    ax.add_patch(FancyBboxPatch((x0,y),w,8,boxstyle="round,pad=0.005,rounding_size=0.02",facecolor=c,edgecolor=c))
    ax.text(x0+w/2,y+4,name,ha="center",va="center",fontsize=8,color="white",weight="bold")
    y-=13
for gx in range(5,96,15):
    ax.add_line(Line2D([gx,gx],[8,80],color="#EEEEEE",lw=1,zorder=0))
ax.text(50,4,"Time  →   (phases overlap; integration and testing run throughout)",ha="center",fontsize=8.5,color=GREY,style="italic")
save(fig,"gantt.png")
print("DONE")
