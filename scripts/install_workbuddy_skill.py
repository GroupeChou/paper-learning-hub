from __future__ import annotations

from pathlib import Path

from paper_learning_hub.config import load_config
from paper_learning_hub.workbuddy import install_skill


def main() -> int:
    config = load_config(Path(__file__).resolve().parent.parent / "config.yaml")
    message = install_skill(config)
    print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

