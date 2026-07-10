"""Keep It Green — full end-to-end logic test (go-live readiness)."""
import time, sys, json
import requests

import os
B = os.environ.get("KIG_BASE", "https://keepitgreen.runasp.net")
MK = "dev-machine-key-change-me"
ok = 0; fail = 0
def check(name, cond, detail=""):
    global ok, fail
    if cond: ok += 1;  print(f"  [PASS] {name}")
    else:    fail += 1; print(f"  [FAIL] {name}  {detail}")

def g(d, *keys, default=None):
    """case-insensitive get"""
    if not isinstance(d, dict): return default
    low = {k.lower(): v for k, v in d.items()}
    for k in keys:
        if k.lower() in low: return low[k.lower()]
    return default

S = requests.Session()
ts = int(time.time())
email = f"tester_{ts}@example.com"; uname = f"tester_{ts}"; pwd = "Test@1234"

print("== 1. Register ==")
r = S.post(f"{B}/api/User/Register", json={"UserName": uname, "Email": email, "Password": pwd})
check("register 2xx", r.status_code // 100 == 2, f"{r.status_code} {r.text[:200]}")

print("== 2. Login ==")
r = S.post(f"{B}/api/User/Login", json={"Email": email, "Password": pwd})
check("login 2xx", r.status_code // 100 == 2, f"{r.status_code} {r.text[:200]}")
token = g(r.json() if r.text else {}, "Token", "token") if r.status_code//100==2 else None
check("got JWT", bool(token))
AUTH = {"Authorization": f"Bearer {token}"}

print("== 3. Initial points ==")
r = S.get(f"{B}/api/User/Coins", headers=AUTH)
coins0 = g(r.json(), "Coins", "coins", default=0) if r.status_code//100==2 else None
check("coins endpoint 2xx", r.status_code//100==2, f"{r.status_code} {r.text[:200]}")
check("new user starts at 0", coins0 == 0, f"got {coins0}")

print("== 4. Machines list ==")
r = S.get(f"{B}/api/Machine", headers=AUTH)
machines = r.json() if r.status_code//100==2 else []
check("machines 2xx + non-empty", r.status_code//100==2 and len(machines) > 0, f"{r.status_code} {r.text[:200]}")
mid = g(machines[0], "Id", "id", default=1) if machines else 1

print("== 5. Machine starts ATM session ==")
r = S.post(f"{B}/api/Detection/session/start", params={"machineId": mid}, headers={"X-Machine-Key": MK})
check("session/start 2xx", r.status_code//100==2, f"{r.status_code} {r.text[:200]}")
sess = r.json() if r.status_code//100==2 else {}
code = g(sess, "PairingCode", "pairingCode")
check("got pairing code", bool(code), str(sess))
check("session has machine name", bool(g(sess, "MachineName", "machineName")), str(sess))
check("session has location", bool(g(sess, "LocationName", "locationName")), str(sess))

print("== 6. Status before pairing ==")
r = S.get(f"{B}/api/Detection/session/{code}/status", headers={"X-Machine-Key": MK})
check("status Paired=false before pair", g(r.json(), "Paired", "paired") == False, r.text[:200])

print("== 7. User pairs with the code (phone) ==")
r = S.post(f"{B}/api/Otp/Pair", json={"Code": code}, headers=AUTH)
check("pair 2xx", r.status_code//100==2, f"{r.status_code} {r.text[:200]}")

print("== 8. Status after pairing ==")
r = S.get(f"{B}/api/Detection/session/{code}/status", headers={"X-Machine-Key": MK})
st = r.json()
check("status Paired=true after pair", g(st, "Paired", "paired") == True, r.text[:200])
check("status carries user name", bool(g(st, "UserName", "userName")), r.text[:200])

print("== 9. Machine submits detections ==")
r = S.post(f"{B}/api/Detection", json={"Otp": code, "ItemType": "Plastic", "ConfidenceScore": 0.93, "ImagePath": ""}, headers={"X-Machine-Key": MK})
check("submit Plastic 2xx", r.status_code//100==2, f"{r.status_code} {r.text[:200]}")
r = S.post(f"{B}/api/Detection", json={"Otp": code, "ItemType": "Aluminum", "ConfidenceScore": 0.88, "ImagePath": ""}, headers={"X-Machine-Key": MK})
check("submit Aluminum 2xx", r.status_code//100==2, f"{r.status_code} {r.text[:200]}")

print("== 10. Session total (machine summary screen) ==")
r = S.get(f"{B}/api/Detection/session/{code}/total", headers={"X-Machine-Key": MK})
total = g(r.json(), "Points", "points")
check("total = 25 (10 plastic + 15 aluminum)", total == 25, f"got {total}")

print("== 11. User transactions ==")
r = S.get(f"{B}/api/Transaction/User", headers=AUTH)
txns = r.json() if r.status_code//100==2 else []
check("transactions show 2 items", isinstance(txns, list) and len(txns) >= 2, f"{r.status_code} got {len(txns) if isinstance(txns,list) else txns}")

print("== 12. Points updated on account ==")
r = S.get(f"{B}/api/User/Coins", headers=AUTH)
coins1 = g(r.json(), "Coins", "coins")
check("coins == 25 after recycling", coins1 == 25, f"got {coins1}")

print("== 13. Reject bad item type ==")
r = S.post(f"{B}/api/Detection", json={"Otp": code, "ItemType": "Banana", "ConfidenceScore": 0.5, "ImagePath": ""}, headers={"X-Machine-Key": MK})
check("invalid item rejected (4xx)", r.status_code//100==4, f"got {r.status_code}")

print("== 14. Reject submission without machine key ==")
r = S.post(f"{B}/api/Detection", json={"Otp": code, "ItemType": "Plastic", "ConfidenceScore": 0.9, "ImagePath": ""})
check("no machine key -> 401", r.status_code == 401, f"got {r.status_code}")

print("== 15. Promos + redeem ==")
r = S.get(f"{B}/api/Promo", headers=AUTH)
promos = r.json() if r.status_code//100==2 else []
check("promos 2xx", r.status_code//100==2, f"{r.status_code} {r.text[:200]}")
affordable = None
for p in (promos or []):
    cost = g(p, "RequiredCoins", "Cost", "Points", "PointsCost", "Price", default=10**9)
    try: cost = float(cost)
    except: cost = 10**9
    if cost <= 25:
        affordable = p; break
if affordable:
    pid = g(affordable, "Id", "id")
    cost = g(affordable, "RequiredCoins", "Cost", "Points", "PointsCost", "Price")
    r = S.post(f"{B}/api/Redemption/{pid}", headers=AUTH)
    check("redeem affordable promo 2xx", r.status_code//100==2, f"{r.status_code} {r.text[:200]}")
    r = S.get(f"{B}/api/User/Coins", headers=AUTH)
    coins2 = g(r.json(), "Coins", "coins")
    check("points deducted after redeem", coins2 is not None and coins2 < coins1, f"before {coins1} after {coins2}")
    r = S.get(f"{B}/api/Redemption/My", headers=AUTH)
    myreds = r.json() if r.status_code//100==2 else []
    check("redemption recorded", isinstance(myreds, list) and len(myreds) >= 1, f"{r.status_code} got {myreds}")
else:
    print(f"  [SKIP] no promo <= 25 pts (promos: {[g(p,'Title','Name') for p in (promos or [])]})")

print("== 16. Reject redeem beyond balance ==")
# try to redeem the most expensive promo (should fail if > balance)
expensive = None; maxc = -1
for p in (promos or []):
    c = g(p, "RequiredCoins", "Cost", "Points", "PointsCost", "Price", default=0)
    try: c = float(c)
    except: c = 0
    if c > maxc: maxc = c; expensive = p
if expensive and maxc > 25:
    r = S.post(f"{B}/api/Redemption/{g(expensive,'Id','id')}", headers=AUTH)
    check("over-balance redeem rejected (4xx)", r.status_code//100==4, f"got {r.status_code} for cost {maxc}")
else:
    print("  [SKIP] no promo expensive enough to test over-balance")

print(f"\n==== RESULT: {ok} passed, {fail} failed ====")
sys.exit(1 if fail else 0)
