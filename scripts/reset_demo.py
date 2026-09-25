from pathlib import Path

from app.services.demo_service import SAFE_PLAYBOOK


def main() -> None:
    Path("app/config/PLAYBOOK.md").write_text(SAFE_PLAYBOOK, encoding="utf-8")
    print("Demo playbook reset.")


if __name__ == "__main__":
    main()
