import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.dev")

import django  # noqa: E402
from django.test import Client  # noqa: E402


def main() -> int:
    django.setup()
    client = Client(HTTP_HOST="127.0.0.1")

    checks = [
        ("/", {301, 302}, "Root should redirect to docs"),
        ("/api/docs/", {200}, "Swagger docs should load"),
        ("/api/schema/", {200}, "Schema should load"),
    ]

    errors: list[str] = []
    for path, expected_statuses, description in checks:
        response = client.get(path)
        status = response.status_code
        print(f"{path} -> {status}")
        if status not in expected_statuses:
            errors.append(f"{description}: expected {sorted(expected_statuses)}, got {status}")

    if errors:
        print("\nSmoke endpoint checks failed:")
        for idx, err in enumerate(errors, start=1):
            print(f"{idx}. {err}")
        return 1

    print("Smoke endpoint checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
