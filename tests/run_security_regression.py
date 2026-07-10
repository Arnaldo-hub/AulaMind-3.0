"""Runner maestro del Bloque 2.4A."""
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

TESTS = [
    "tests.auth_session_regression",
    "tests.csrf_regression",
    "tests.authorization_integrity",
    "tests.password_reset_integrity",
    "tests.staging_security_config",
    "tests.rate_limit_regression",
]


def run():
    results = []

    for module_name in TESTS:
        print("\n" + "=" * 72)
        print(f"RUN {module_name}")
        print("=" * 72)

        completed = subprocess.run(
            [sys.executable, "-m", module_name],
            cwd=str(ROOT),
            text=True,
        )

        status = "PASS" if completed.returncode == 0 else "FAIL"
        results.append((module_name, status))

    print("\n" + "=" * 72)
    print("AULAMIND SECURITY REGRESSION SUMMARY")
    print("=" * 72)

    for name, status in results:
        print(f"{status:4}  {name}")

    failed = [name for name, status in results if status == "FAIL"]

    if failed:
        print(f"\nSECURITY REGRESSION FAILED: {len(failed)} test(s)")
        return 1

    print(f"\nSECURITY REGRESSION OK: {len(results)} test(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
