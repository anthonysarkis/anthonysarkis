"""Redraws farm.svg from my GitHub commits.

Run: ACCESS_TOKEN=<token> uv run update_profile.py
"""

import os
import sys
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from art.farm import farm_svg
from art.report import report_label
from harvest.commits import fetch_commits
from harvest.github import GitHub
from harvest.stats import summarize

LOGIN = "anthonysarkis"
BORN = date(2000, 7, 28)
BEDTIME = "6:22 am"
MONTREAL = ZoneInfo("America/Toronto")

ROOT = Path(__file__).parent
PICTURE = ROOT / "farm.svg"
COUNTED_COMMITS = ROOT / "counted-commits.json"


def main() -> None:
    token = read_token()
    github = GitHub(token)

    commits = fetch_commits(github, LOGIN, MONTREAL, COUNTED_COMMITS)
    if not commits:
        sys.exit(f"No commits by {LOGIN} found. Can the token read your repositories?")

    today = datetime.now(MONTREAL).date()
    harvest = summarize(commits, today, BORN, BEDTIME)
    picture = farm_svg(harvest)
    PICTURE.write_text(picture, encoding="utf-8")

    summary = report_label(harvest)
    print(summary)


def read_token() -> str:
    token = os.environ.get("ACCESS_TOKEN")
    if not token:
        sys.exit("Set ACCESS_TOKEN to a GitHub token that can read your repositories.")
    return token


if __name__ == "__main__":
    main()
