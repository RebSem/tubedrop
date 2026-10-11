"""tubedrop entry point. Only the web UI is supported."""
import argparse
import os
import sys
import warnings
from pathlib import Path

# Quiet the urllib3/LibreSSL deprecation warning in case the user is running
# on an older Python. install.command normally bundles 3.12, so this is a
# belt-and-suspenders thing.
warnings.filterwarnings("ignore")
os.environ.setdefault("PYTHONWARNINGS", "ignore")

sys.path.insert(0, str(Path(__file__).parent.parent))


def main():
    parser = argparse.ArgumentParser(
        prog="tubedrop",
        description="tubedrop — local YouTube & VK Video downloader with a web UI.",
    )
    parser.add_argument(
        "-W", "-w", "--web",
        action="store_true",
        default=True,
        help="Launch the web UI (default).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Override the default port (8765).",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Don't auto-open the browser on launch.",
    )
    parser.add_argument(
        "--no-update",
        action="store_true",
        help="Skip the daily yt-dlp update check.",
    )
    args = parser.parse_args()

    # Must run before yt_dlp is imported anywhere in this process.
    if not args.no_update:
        from ytconverter.updater import maybe_update
        maybe_update()

    from ytconverter.web.server import serve
    serve(open_browser=not args.no_browser, port=args.port)


if __name__ == "__main__":
    main()
