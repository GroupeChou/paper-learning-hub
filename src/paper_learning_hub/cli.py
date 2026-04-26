from __future__ import annotations

import argparse
from pathlib import Path

from .pipeline import Pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Paper learning hub pipeline")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    parser.add_argument("--discover-only", action="store_true", help="Only discover and persist candidate papers")
    parser.add_argument("--build-only", action="store_true", help="Only rebuild guides and the MkDocs site")
    parser.add_argument(
        "--prepare-workbuddy",
        action="store_true",
        help="Discover/download papers and generate WorkBuddy job briefs instead of direct translation",
    )
    parser.add_argument(
        "--sync-workbuddy",
        action="store_true",
        help="Only ingest completed WorkBuddy outputs into the database",
    )
    parser.add_argument(
        "--install-workbuddy-skill",
        action="store_true",
        help="Install or refresh the local WorkBuddy skill symlink for this project",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    pipeline = Pipeline(Path(args.config))
    try:
        result = pipeline.run(
            discover_only=args.discover_only,
            build_only=args.build_only,
            prepare_workbuddy_only=args.prepare_workbuddy,
            sync_workbuddy_only=args.sync_workbuddy,
            install_workbuddy_skill_only=args.install_workbuddy_skill,
        )
    finally:
        pipeline.close()
    print(
        f"discovered={result.discovered} downloaded={result.downloaded} translated={result.translated} "
        f"queued={result.queued} failed={result.failed} site_built={result.site_built}"
    )
    if result.git_message:
        print(result.git_message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
