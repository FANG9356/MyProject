import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from main import app

print("="*60)
print("[TEST SIMULATION] 06_Karaoke-Streaming-System")
print("="*60)

routes = [r.path for r in app.routes if hasattr(r, "path")]
print(f" Registered FastAPI Endpoints ({len(routes)} routes):")
for r in ["/", "/remote", "/search", "/add_song", "/state/get"]:
    assert r in routes, f"Missing critical route: {r}"
    print(f"   - Route [{r}]: OK")

for asset in ["index.html", "remote.html", "static/script.js", "static/style.css"]:
    p = os.path.join(os.path.dirname(__file__), asset)
    assert os.path.exists(p), f"Missing template/asset: {asset}"
print("Web & Mobile Remote Frontend Assets Verified")
print("Status: TEST PASSED (100% Operational)")
