"""Multi-user OTP isolation: do two users on the SAME machine stay separate?"""
import time, sys, requests
import os
B = os.environ.get("KIG_BASE", "https://keepitgreen.runasp.net")
MK = {"X-Machine-Key": "dev-machine-key-change-me"}
ok = 0; fail = 0
def check(n, c, d=""):
    global ok, fail
    print(("  [PASS] " if c else "  [FAIL] ") + n + ("" if c else f"   {d}"))
    ok += c; fail += (not c)
def g(x, *ks, default=None):
    if not isinstance(x, dict): return default
    low = {k.lower(): v for k, v in x.items()}
    for k in ks:
        if k.lower() in low: return low[k.lower()]
    return default

def new_user(tag):
    ts = time.time_ns()
    em = f"{tag}_{ts}@x.com"
    s = requests.Session()
    s.post(f"{B}/api/User/Register", json={"UserName": f"{tag}{ts%100000}", "Email": em, "Password": "Test@1234"})
    tok = g(s.post(f"{B}/api/User/Login", json={"Email": em, "Password": "Test@1234"}).json(), "Token")
    return s, {"Authorization": f"Bearer {tok}"}

def start_code(mid=None):
    mid = mid if mid is not None else MID
    return g(requests.post(f"{B}/api/Detection/session/start", params={"machineId": mid}, headers=MK).json(), "PairingCode")


# discover the live machine's real (auto-increment) id
_as=requests.Session()
_atok=g(_as.post(f"{B}/api/User/Login",json={"Email":"admin@recycle.com","Password":os.environ.get("KIG_ADMIN_PW", "Admin@123")}).json(),"Token")
_ms=_as.get(f"{B}/api/Machine",headers={"Authorization":f"Bearer {_atok}"}).json()
MID=g(_ms[0],"Id","id") if _ms else 1
print("using machine id:",MID)

print("== Two users, same machine, ATM-pair flow ==")
Sa, A = new_user("alice")
Sb, Bh = new_user("bob")
codeA = start_code(); codeB = start_code()
check("each machine session gets a UNIQUE code", codeA != codeB, f"{codeA} vs {codeB}")
requests.post(f"{B}/api/Otp/Pair", json={"Code": codeA}, headers=A)
requests.post(f"{B}/api/Otp/Pair", json={"Code": codeB}, headers=Bh)

# machine credits each code to its own owner
requests.post(f"{B}/api/Detection", json={"Otp": codeA, "ItemType": "Plastic",  "ConfidenceScore": 0.95, "ImagePath": ""}, headers=MK)   # +10 -> A
requests.post(f"{B}/api/Detection", json={"Otp": codeA, "ItemType": "Plastic",  "ConfidenceScore": 0.95, "ImagePath": ""}, headers=MK)   # +10 -> A
requests.post(f"{B}/api/Detection", json={"Otp": codeB, "ItemType": "Aluminum", "ConfidenceScore": 0.95, "ImagePath": ""}, headers=MK)   # +15 -> B

coinsA = g(Sa.get(f"{B}/api/User/Coins", headers=A).json(), "Coins")
coinsB = g(Sb.get(f"{B}/api/User/Coins", headers=Bh).json(), "Coins")
check("Alice credited ONLY her 2 plastics (20)", coinsA == 20, f"got {coinsA}")
check("Bob credited ONLY his 1 aluminum (15)", coinsB == 15, f"got {coinsB}")

# per-code session total resolves to the right user
totA = g(requests.get(f"{B}/api/Detection/session/{codeA}/total", headers=MK).json(), "Points")
totB = g(requests.get(f"{B}/api/Detection/session/{codeB}/total", headers=MK).json(), "Points")
check("codeA total == Alice's balance", totA == coinsA, f"{totA} vs {coinsA}")
check("codeB total == Bob's balance", totB == coinsB, f"{totB} vs {coinsB}")

# machine correctly knows WHOSE session each code is
sa = requests.get(f"{B}/api/Detection/session/{codeA}/status", headers=MK).json()
sb = requests.get(f"{B}/api/Detection/session/{codeB}/status", headers=MK).json()
check("codeA status shows a paired user", g(sa, "Paired"), str(sa))
check("codeB status shows a paired user", g(sb, "Paired"), str(sb))
check("the two codes map to DIFFERENT users", g(sa, "UserName") != g(sb, "UserName"), f"{g(sa,'UserName')} vs {g(sb,'UserName')}")

print("== A code already paired to Alice cannot be hijacked by Bob ==")
codeC = start_code()
r1 = requests.post(f"{B}/api/Otp/Pair", json={"Code": codeC}, headers=A)   # Alice pairs
r2 = requests.post(f"{B}/api/Otp/Pair", json={"Code": codeC}, headers=Bh)  # Bob tries the same code
check("Alice pairs codeC (2xx)", r1.status_code // 100 == 2, f"{r1.status_code}")
check("Bob is REJECTED from Alice's code (4xx)", r2.status_code // 100 == 4, f"{r2.status_code} {r2.text[:120]}")

print("== User-generated OTP flow (Otp/Generate) also isolates ==")
otpA = g(Sa.get(f"{B}/api/Otp/Generate/{MID}", headers=A).json(), "Otp")
otpB = g(Sb.get(f"{B}/api/Otp/Generate/{MID}", headers=Bh).json(), "Otp")
check("two users get DIFFERENT generated OTPs", otpA != otpB, f"{otpA} vs {otpB}")
beforeA = g(Sa.get(f"{B}/api/User/Coins", headers=A).json(), "Coins")
requests.post(f"{B}/api/Detection", json={"Otp": otpA, "ItemType": "Aluminum", "ConfidenceScore": 0.95, "ImagePath": ""}, headers=MK)  # +15 -> A
afterA = g(Sa.get(f"{B}/api/User/Coins", headers=A).json(), "Coins")
afterB = g(Sb.get(f"{B}/api/User/Coins", headers=Bh).json(), "Coins")
check("Alice's own OTP credited Alice (+15)", afterA - beforeA == 15, f"{beforeA}->{afterA}")
check("Bob's balance untouched by Alice's OTP", afterB == coinsB, f"{afterB} vs {coinsB}")

print(f"\n==== ISOLATION RESULT: {ok} passed, {fail} failed ====")
sys.exit(1 if fail else 0)
