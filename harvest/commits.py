import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import NamedTuple
from zoneinfo import ZoneInfo

from .counted_commits import load_counts, save_counts
from .github import GitHub
from .lines import LineCount, count_lines

REPOSITORIES_PATH = "/user/repos?affiliation=owner,collaborator,organization_member&per_page=100"
PARALLEL_REQUESTS = 6

SKIPPED_COMMITS = {
    "ff988af0f1165d68a2621496e4ee8ce66b4bd5b7": "Poly-AntennaPod: upstream AntennaPod import",
    "ac217c96ddf98dc625c6e5216453363c4ad963ee": "LOG8235-Exercices: Unreal starter project",
}


class ListedCommit(NamedTuple):
    repository: str
    sha: str
    authored_at: datetime


class Commit(NamedTuple):
    repository: str
    local_time: datetime
    lines_added: int
    lines_removed: int


def fetch_commits(github: GitHub, login: str, time_zone: ZoneInfo, counts_path: Path) -> list[Commit]:
    listed = list_commits(github, login)
    if not listed:
        return []

    saved_counts = load_counts(counts_path)
    new_counts = count_new_commits(github, listed, saved_counts)
    counts = saved_counts | new_counts

    counts_to_keep = exact_counts_still_listed(counts, listed)
    save_counts(counts_path, counts_to_keep)

    return [localize(commit, counts[commit.sha], time_zone) for commit in listed]


def list_commits(github: GitHub, login: str) -> list[ListedCommit]:
    repositories = github.get_all_pages(REPOSITORIES_PATH)
    own_repositories = [repository["full_name"] for repository in repositories if not repository["fork"]]

    listed = []
    for repository in own_repositories:
        repository_commits = list_repository_commits(github, repository, login)
        listed.extend(repository_commits)

    return listed


def list_repository_commits(github: GitHub, repository: str, login: str) -> list[ListedCommit]:
    commits = github.get_all_pages(f"/repos/{repository}/commits?author={login}&per_page=100")
    return [to_listed_commit(repository, commit) for commit in commits if should_count(commit)]


def should_count(commit: dict) -> bool:
    is_merge = len(commit["parents"]) > 1
    return not is_merge and commit["sha"] not in SKIPPED_COMMITS


def to_listed_commit(repository: str, commit: dict) -> ListedCommit:
    authored_at = datetime.fromisoformat(commit["commit"]["author"]["date"])
    return ListedCommit(repository, commit["sha"], authored_at)


def count_new_commits(
    github: GitHub, listed: list[ListedCommit], saved_counts: dict[str, LineCount]
) -> dict[str, LineCount]:
    to_count = [commit for commit in listed if commit.sha not in saved_counts]

    with ThreadPoolExecutor(PARALLEL_REQUESTS) as pool:
        counts = list(pool.map(lambda commit: count_lines(github, commit.repository, commit.sha), to_count))

    for commit, count in zip(to_count, counts, strict=True):
        if not count.exact:
            print(f"No file list for {commit.repository}@{commit.sha[:7]}, estimated for now", file=sys.stderr)

    print(f"{len(listed):,} commits, {len(to_count):,} counted this run", file=sys.stderr)
    return {commit.sha: count for commit, count in zip(to_count, counts, strict=True)}


def exact_counts_still_listed(counts: dict[str, LineCount], listed: list[ListedCommit]) -> dict[str, LineCount]:
    listed_shas = {commit.sha for commit in listed}
    return {sha: count for sha, count in counts.items() if sha in listed_shas and count.exact}


def localize(commit: ListedCommit, count: LineCount, time_zone: ZoneInfo) -> Commit:
    local_time = commit.authored_at.astimezone(time_zone)
    return Commit(commit.repository, local_time, count.added, count.removed)
