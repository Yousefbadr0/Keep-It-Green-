"""Keep It Green — admin-flow test (validates the mobile Admin panel endpoints)."""
import time, sys, json, base64
import requests

import os
B = os.environ.get("KIG_BASE", "https://keepitgreen.runasp.net")
ok = 0; fail = 0
def check(name, cond, detail=""):
    global ok, fail
    if cond: ok += 1;  print(f"  [PASS] {name}")
    else:    fail += 1; print(f"  [FAIL] {name}  {detail}")

def g(d, *keys, default=None):
    if not isinstance(d, dict): return default
    low = {k.lower(): v for k, v in d.items()}
    for k in keys:
        if k.lower() in low: return low[k.lower()]
    return default

def jwt_payload(tok):
    p = tok.split('.')[1]
    p += '=' * (-len(p) % 4)
    return json.loads(base64.urlsafe_b64decode(p))

S = requests.Session()

print("== Admin login ==")
r = S.post(f"{B}/api/User/Login", json={"Email": "admin@recycle.com", "Password": os.environ.get("KIG_ADMIN_PW", "Admin@123")})
check("admin login 2xx", r.status_code // 100 == 2, f"{r.status_code} {r.text[:200]}")
tok = g(r.json(), "Token") if r.status_code // 100 == 2 else None
check("got admin JWT", bool(tok))
A = {"Authorization": f"Bearer {tok}"}

print("== JWT carries the Admin role (so mobile isAdmin works) ==")
payload = jwt_payload(tok) if tok else {}
role_vals = []
for k, v in payload.items():
    kl = k.lower()
    if kl == 'role' or kl == 'roles' or kl.endswith('/role') or kl.endswith('/roles'):
        role_vals += v if isinstance(v, list) else [v]
print(f"     role claim keys -> {[k for k in payload if 'role' in k.lower()]}")
check("Admin role present in JWT", any(str(x).lower() == 'admin' for x in role_vals), f"roles={role_vals}")

print("== Machines: add / toggle / delete ==")
name = f"TestMachine_{int(time.time())}"
r = S.post(f"{B}/api/Machine", headers=A, json={"Name": name, "Location": "Giza", "IsAvailable": True})
check("add machine 2xx", r.status_code // 100 == 2, f"{r.status_code} {r.text[:200]}")
r = S.get(f"{B}/api/Machine", headers=A)
machines = r.json() if r.status_code // 100 == 2 else []
mine = next((m for m in machines if g(m, "Name", "name") == name), None)
check("added machine appears in list", mine is not None)
if mine:
    mid = g(mine, "Id", "id")
    r = S.put(f"{B}/api/Machine/{mid}", headers=A, json={"IsAvailable": False})
    check("update machine status 2xx", r.status_code // 100 == 2, f"{r.status_code} {r.text[:200]}")
    r = S.get(f"{B}/api/Transaction/Admin/{mid}", headers=A)
    check("admin transactions endpoint 2xx", r.status_code // 100 == 2, f"{r.status_code} {r.text[:200]}")
    r = S.delete(f"{B}/api/Machine/{mid}", headers=A)
    check("delete machine 2xx", r.status_code // 100 == 2, f"{r.status_code} {r.text[:200]}")

print("== Vendors + Promo ==")
vname = f"TestVendor_{int(time.time())}"
r = S.post(f"{B}/api/Vendor", headers=A, json={"Name": vname, "Email": f"v{int(time.time())}@x.com", "Description": "test"})
check("add vendor 2xx", r.status_code // 100 == 2, f"{r.status_code} {r.text[:200]}")
r = S.get(f"{B}/api/Vendor", headers=A)
vendors = r.json() if r.status_code // 100 == 2 else []
check("vendors list 2xx + non-empty", isinstance(vendors, list) and len(vendors) > 0, f"{r.status_code}")
mineV = next((v for v in vendors if g(v, "Name", "name") == vname), None)
if mineV:
    vid = g(mineV, "Id", "id")
    r = S.post(f"{B}/api/Promo", headers=A, json={
        "VendorId": vid, "Code": f"TEST{int(time.time())}", "RequiredCoins": 40,
        "ExpirationDate": "2027-01-01T00:00:00", "UsageLimit": 5})
    check("add promo 2xx", r.status_code // 100 == 2, f"{r.status_code} {r.text[:200]}")

print("== A normal USER is rejected from admin endpoints (403) ==")
ts = int(time.time())
S.post(f"{B}/api/User/Register", json={"UserName": f"u_{ts}", "Email": f"u_{ts}@x.com", "Password": "Test@1234"})
ur = S.post(f"{B}/api/User/Login", json={"Email": f"u_{ts}@x.com", "Password": "Test@1234"})
utok = g(ur.json(), "Token")
r = S.post(f"{B}/api/Machine", headers={"Authorization": f"Bearer {utok}"}, json={"Name": "x", "Location": "y", "IsAvailable": True})
check("user add machine -> 403", r.status_code == 403, f"got {r.status_code}")

print(f"\n==== ADMIN RESULT: {ok} passed, {fail} failed ====")
sys.exit(1 if fail else 0)
