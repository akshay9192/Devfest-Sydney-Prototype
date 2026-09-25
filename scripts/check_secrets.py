from __future__ import annotations

import re
import shutil
# This script invokes only a resolved git executable with constant arguments.
import subprocess  # nosec B404
from pathlib import Path

PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "Google API key": re.compile(r"AIza[0-9A-Za-z_-]{35}"),
    "GitHub token": re.compile(r"gh[pousr]_[0-9A-Za-z]{30,}"),
    "generic bearer token": re.compile(r"(?i)authorization\s*[:=]\s*bearer\s+[A-Za-z0-9._-]{20,}"),
}


def tracked_files() -> list[Path]:
    git = shutil.which("git")
    if git is None:
        raise SystemExit("git is required for the secret scan")
    # The executable is resolved from the trusted PATH and arguments are constant.
    result = subprocess.run(  # noqa: S603  # nosec B603
        [git, "ls-files", "--cached", "--others", "--exclude-standard"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [Path(line) for line in result.stdout.splitlines() if line]


def main() -> None:
    findings: list[str] = []
    for path in tracked_files():
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for name, pattern in PATTERNS.items():
            if pattern.search(text):
                findings.append(f"{path}: possible {name}")
    if findings:
        raise SystemExit("\n".join(findings))
    print("No forbidden secret patterns found.")


if __name__ == "__main__":
    main()
