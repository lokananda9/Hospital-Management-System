import sys
import time
import urllib.request

URL = "http://127.0.0.1:8000/api/schema/"

for _ in range(20):
    try:
        with urllib.request.urlopen(URL, timeout=1) as response:
            print(response.status)
            sys.exit(0)
    except Exception:
        time.sleep(0.5)

print("DOWN")
sys.exit(1)
