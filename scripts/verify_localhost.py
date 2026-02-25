import subprocess
import sys
import time
import urllib.request


def main() -> int:
    proc = subprocess.Popen(
        [sys.executable, "-u", "manage.py", "runserver", "127.0.0.1:8000", "--noreload"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        for _ in range(40):
            if proc.poll() is not None:
                print("runserver exited before becoming reachable.")
                return 1
            try:
                with urllib.request.urlopen("http://127.0.0.1:8000/api/schema/", timeout=1) as response:
                    print(f"Localhost check status: {response.status}")
                    return 0
            except Exception:
                time.sleep(0.5)

        print("Could not reach localhost endpoint within timeout.")
        return 1
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


if __name__ == "__main__":
    raise SystemExit(main())
