import argparse
import importlib
import os
import shutil
import socket
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT_DIR / ".env"
DEFAULT_PORT = 8000


def parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def read_setting(key: str, env_values: dict[str, str], default: str = "") -> str:
    return os.getenv(key, env_values.get(key, default))


def print_errors(errors: list[str], warnings: list[str] | None = None) -> int:
    print("Preflight failed:")
    for idx, item in enumerate(errors, start=1):
        print(f"{idx}. {item}")
    if warnings:
        print("\nWarnings:")
        for idx, item in enumerate(warnings, start=1):
            print(f"{idx}. {item}")
    return 1


def parse_host(url: str) -> str:
    try:
        return (urlparse(url).hostname or "").lower()
    except Exception:
        return ""


def run_manage_check(python_executable: str) -> tuple[int, str]:
    try:
        result = subprocess.run(
            [python_executable, "manage.py", "check"],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        return 1, f"Failed to execute '{python_executable}': {exc}"
    output = (result.stdout or "") + (result.stderr or "")
    return result.returncode, output.strip()


def normalize_executable(value: str) -> str:
    return value.strip().strip('"').strip("'")


def validate_python_executable(python_executable: str) -> str | None:
    normalized = normalize_executable(python_executable)
    candidate = Path(normalized)
    if candidate.exists():
        return str(candidate)
    resolved = shutil.which(normalized)
    if resolved:
        return resolved
    return None


def can_import_modules_locally(modules: tuple[str, ...]) -> list[str]:
    missing: list[str] = []
    for module in modules:
        try:
            importlib.import_module(module)
        except Exception:
            missing.append(module)
    return missing


def can_import_modules_with_python(python_executable: str, modules: tuple[str, ...]) -> list[str]:
    script_lines = [
        "import importlib,sys",
        "missing=[]",
        f"mods={list(modules)!r}",
        "for m in mods:",
        "    try: importlib.import_module(m)",
        "    except Exception: missing.append(m)",
        "print(','.join(missing))",
    ]
    result = subprocess.run(
        [python_executable, "-c", "\n".join(script_lines)],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return list(modules)
    line = (result.stdout or "").strip()
    if not line:
        return []
    return [item for item in line.split(",") if item]


def check_port_warning(port: int) -> str | None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.3)
    try:
        if sock.connect_ex(("127.0.0.1", port)) == 0:
            return (
                f"Port {port} appears to be in use. "
                f"If startup fails, run server on another port: 127.0.0.1:{port + 1}"
            )
    except Exception:
        return None
    finally:
        sock.close()
    return None


def run_native_checks(python_executable: str) -> int:
    errors: list[str] = []
    warnings: list[str] = []
    env_values = parse_env_file(ENV_PATH)
    modules = ("django", "dj_database_url", "rest_framework")
    python_executable = normalize_executable(python_executable)

    resolved_python = validate_python_executable(python_executable)
    if not resolved_python:
        errors.append(
            f"Python executable not found: {python_executable}. "
            "Run scripts\\run_native.cmd to initialize .venv."
        )
    else:
        version_result = subprocess.run(
            [resolved_python, "--version"],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
        )
        if version_result.returncode != 0:
            errors.append(f"Failed to execute Python: {resolved_python}")

    if not errors:
        missing_modules = (
            can_import_modules_locally(modules)
            if Path(resolved_python or "").resolve() == Path(sys.executable).resolve()
            else can_import_modules_with_python(resolved_python, modules)
        )
        for module in missing_modules:
            errors.append(
                f"Missing dependency '{module}'. Run: python -m pip install -r requirements.txt"
            )

    if not ENV_PATH.exists():
        errors.append("Missing .env. Run: copy .env.native.example .env")

    database_url = read_setting("DATABASE_URL", env_values, "")
    db_host = parse_host(database_url) if database_url else ""
    if db_host == "db":
        errors.append(
            "DATABASE_URL points to Docker host 'db', which is invalid for native mode. "
            "Use sqlite:///db.sqlite3 or local PostgreSQL host."
        )

    redis_url = read_setting("REDIS_URL", env_values, "")
    redis_host = parse_host(redis_url) if redis_url else ""
    if redis_host in {"redis", "db"}:
        errors.append(
            "REDIS_URL points to Docker service host. For native mode, clear REDIS_URL "
            "or set a reachable host such as redis://127.0.0.1:6379/1."
        )

    port_warning = check_port_warning(DEFAULT_PORT)
    if port_warning:
        warnings.append(port_warning)

    status, output = run_manage_check(resolved_python or python_executable)
    if status != 0:
        errors.append(
            f"Django check failed. Run: {resolved_python or python_executable} manage.py check\n{output}"
        )

    if errors:
        return print_errors(errors, warnings)

    print("Preflight checks passed for mode: native")
    if warnings:
        print("\nWarnings:")
        for idx, item in enumerate(warnings, start=1):
            print(f"{idx}. {item}")
    return 0


def run_docker_checks() -> int:
    errors: list[str] = []
    env_values = parse_env_file(ENV_PATH)

    if not shutil.which("docker"):
        errors.append(
            "Docker command not found. Install Docker Desktop and restart terminal. "
            "Verify with: docker --version"
        )
    else:
        docker_result = subprocess.run(
            ["docker", "--version"],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
        )
        if docker_result.returncode != 0:
            errors.append(
                "Docker is installed but not responding correctly. "
                "Verify Docker Desktop is running and retry."
            )

        compose_result = subprocess.run(
            ["docker", "compose", "version"],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
        )
        if compose_result.returncode != 0:
            errors.append(
                "Docker Compose plugin is unavailable. Update Docker Desktop and verify with: "
                "docker compose version"
            )

    if not ENV_PATH.exists():
        errors.append("Missing .env. Run: copy .env.docker.example .env")
    else:
        database_url = read_setting("DATABASE_URL", env_values, "")
        if not database_url:
            errors.append("DATABASE_URL is required for Docker mode.")
        else:
            parsed_db = urlparse(database_url)
            db_scheme = (parsed_db.scheme or "").lower()
            db_host = (parsed_db.hostname or "").lower()
            if db_scheme.startswith("sqlite"):
                errors.append("DATABASE_URL must not use sqlite in Docker mode.")
            if db_host != "db":
                errors.append(
                    "DATABASE_URL host should be 'db' for docker-compose networking."
                )

        redis_url = read_setting("REDIS_URL", env_values, "")
        if not redis_url:
            errors.append("REDIS_URL is required for Docker mode.")
        else:
            redis_host = parse_host(redis_url)
            if redis_host != "redis":
                errors.append(
                    "REDIS_URL host should be 'redis' for docker-compose networking."
                )

    if errors:
        return print_errors(errors)

    print("Preflight checks passed for mode: docker")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate local startup prerequisites.")
    parser.add_argument("--mode", choices=["native", "docker"], required=True)
    parser.add_argument(
        "--python-executable",
        default=sys.executable,
        help="Python executable path used for native checks and manage.py check.",
    )
    args = parser.parse_args()

    if args.mode == "native":
        return run_native_checks(args.python_executable)
    return run_docker_checks()


if __name__ == "__main__":
    raise SystemExit(main())
