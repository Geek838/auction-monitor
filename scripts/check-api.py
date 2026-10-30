"""Run offline backend checks with useful diagnostics and a finite CI deadline."""
from pathlib import Path
import os
import signal
import subprocess
import sys


def main() -> int:
    repository = Path(__file__).resolve().parent.parent
    suites = ["services/api/tests"]
    if (repository / "tools/tests").is_dir():
        suites.append("tools/tests")
    command = [
        sys.executable, "-m", "pytest", *suites,
        "-vv", "--durations=10", "-o", "faulthandler_timeout=60",
        "--junitxml=.cache/qa/backend-results.xml",
    ]
    # Isolate this invocation so timeout cleanup never targets unrelated servers.
    options = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt" else {"start_new_session": True}
    with subprocess.Popen(command, cwd=repository, **options) as process:
        try:
            return process.wait(timeout=300)
        except subprocess.TimeoutExpired:
            print("Backend checks exceeded five minutes. Inspect the last test and faulthandler stack above.", file=sys.stderr)
            if os.name == "nt":
                # The PID belongs to the subprocess just started above.
                subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], timeout=30, check=False)
            else:
                os.killpg(process.pid, signal.SIGKILL)
            process.wait(timeout=30)
            return 1


if __name__ == "__main__":
    raise SystemExit(main())
