from __future__ import annotations

import argparse
import os

import uvicorn


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the DevFest demonstration")
    parser.add_argument("--mode", choices=("offline_demo", "live"), default="offline_demo")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    os.environ["APP_MODE"] = args.mode
    uvicorn.run("app.main:app", host=args.host, port=args.port, access_log=False)


if __name__ == "__main__":
    main()
