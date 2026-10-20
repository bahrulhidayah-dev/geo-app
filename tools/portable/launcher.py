# launcher.py - starts GeoChem App from the portable folder.
# Finds a free port, starts the app server and opens the default browser.
# Part of GeoChem App (GPL-3.0).
import os
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path

HERE = Path(__file__).resolve().parent
APP = HERE / "app" / "app.py"


def free_port(start=8501, tries=50):
    for port in range(start, start + tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise SystemExit("No free port between 8501 and 8550. Close other apps and try again.")


def open_browser_when_ready(port, url):
    for _ in range(240):                  # up to 2 minutes on a slow computer
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                break
        except OSError:
            time.sleep(0.5)
    time.sleep(1.0)
    webbrowser.open(url)


def main():
    if not APP.exists():
        raise SystemExit(f"App not found: {APP}")
    port = free_port()
    url = f"http://localhost:{port}"
    print("=" * 64)
    print(" GeoChem App is starting ...")
    print(f" Your browser will open {url}")
    print(" Keep this window open while you use the app.")
    print(" To stop the app, close this window.")
    print("=" * 64)
    threading.Thread(target=open_browser_when_ready, args=(port, url), daemon=True).start()
    os.chdir(APP.parent)                  # so .streamlit/config.toml is used
    os.environ.setdefault("STREAMLIT_BROWSER_GATHER_USAGE_STATS", "false")
    from streamlit.web import cli
    sys.argv = ["streamlit", "run", str(APP),
                "--server.headless", "true",
                "--server.address", "localhost",
                "--server.port", str(port),
                "--browser.gatherUsageStats", "false",
                "--global.developmentMode", "false"]
    sys.exit(cli.main())


if __name__ == "__main__":
    main()
