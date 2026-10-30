"""Exercise the documented Windows launchers against real loopback servers."""
from contextlib import ExitStack
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import ProxyHandler, build_opener


def main() -> int:
    if os.name != "nt":
        print("This smoke check requires native Windows.", file=sys.stderr)
        return 1
    repository = Path(__file__).resolve().parent.parent
    evidence = repository / ".cache/qa"
    evidence.mkdir(parents=True, exist_ok=True)
    processes = []
    opener = build_opener(ProxyHandler({}))
    for port in (8000, 3000):
        with socket.socket() as probe:
            probe.settimeout(1)
            if probe.connect_ex(("127.0.0.1", port)) == 0:
                raise RuntimeError(f"Port {port} is occupied; this smoke check must start its own servers.")

    def wait_for(url, process, expected):
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError(f"Launcher exited before {url} was ready; inspect Windows smoke logs.")
            try:
                with opener.open(url, timeout=2) as response:
                    body = response.read(512 * 1024).decode("utf-8")
                    if response.status == 200 and expected(body):
                        return
            except (URLError, TimeoutError):
                pass
            time.sleep(0.25)
        raise RuntimeError(f"Server did not become ready within 60 seconds: {url}")

    try:
        with ExitStack() as files:
            for name, arguments in [("api", ["-NoReload"]), ("web", ["-Production"])]:
                log = files.enter_context((evidence / f"windows-smoke-{name}.log").open("wb"))
                process = subprocess.Popen(
                    ["powershell.exe", "-NoProfile", "-NonInteractive", "-File",
                     str(repository / f"scripts/start-{name}.ps1"), *arguments],
                    cwd=repository, stdout=log, stderr=subprocess.STDOUT,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                )
                processes.append(process)
                if name == "api":
                    wait_for("http://127.0.0.1:8000/api/v1/health", process,
                             lambda body: json.loads(body).get("provider") == "FIXTURE")
                else:
                    wait_for("http://127.0.0.1:3000/", process, lambda body: "Auction Intelligence" in body)
                    wait_for("http://127.0.0.1:3000/api/v1/health", process,
                             lambda body: json.loads(body).get("provider") == "FIXTURE")
            print("Windows launchers served the API, production homepage and API proxy successfully.")
    finally:
        for process in reversed(processes):
            if process.poll() is None:
                subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], timeout=30, check=False)
                process.wait(timeout=30)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
