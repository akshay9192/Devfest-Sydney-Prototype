from pathlib import Path

from app.services.demo_service import POISON_BLOCK
from app.services.proposer import POISON_MARKER


def main() -> None:
    path = Path("app/config/PLAYBOOK.md")
    current = path.read_text(encoding="utf-8")
    if POISON_MARKER not in current:
        path.write_text(current.rstrip() + POISON_BLOCK, encoding="utf-8")
    print("PLAYBOOK.md poisoned; SYSTEM_POLICY.yaml was not modified.")


if __name__ == "__main__":
    main()
