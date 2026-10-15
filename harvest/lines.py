import hashlib
import re
from pathlib import PurePosixPath
from typing import NamedTuple

from .github import GitHub

CODE_EXTENSIONS = frozenset(
    {
        ".ts",
        ".tsx",
        ".mts",
        ".cts",
        ".js",
        ".jsx",
        ".mjs",
        ".cjs",
        ".py",
        ".java",
        ".kt",
        ".kts",
        ".c",
        ".h",
        ".cpp",
        ".cc",
        ".cxx",
        ".hpp",
        ".hh",
        ".cs",
        ".go",
        ".rs",
        ".rb",
        ".php",
        ".swift",
        ".dart",
        ".scala",
        ".r",
        ".sql",
        ".plpgsql",
        ".sh",
        ".bash",
        ".zsh",
        ".html",
        ".htm",
        ".css",
        ".scss",
        ".sass",
        ".less",
        ".vue",
        ".svelte",
        ".lua",
        ".asm",
        ".s",
        ".vhd",
        ".vhdl",
        ".m",
    }
)

SKIPPED_FILE_NAMES = frozenset(
    {
        "package-lock.json",
        "yarn.lock",
        "pnpm-lock.yaml",
        "bun.lockb",
        "poetry.lock",
        "Pipfile.lock",
        "Cargo.lock",
        "Gemfile.lock",
        "composer.lock",
        "go.sum",
    }
)

SKIPPED_PATH = re.compile(
    r"(^|/)(node_modules|vendor|third_party|libs|dist|build|out|\.next|coverage|__pycache__|venv|\.venv|\.obsidian)/"
    r"|\.min\.(js|css)$|\.generated\.\w+$"
)

FILES_PER_PAGE = 300


class LineCount(NamedTuple):
    added: int
    removed: int
    exact: bool = True


def fingerprint_rules() -> str:
    rules = repr((sorted(CODE_EXTENSIONS), sorted(SKIPPED_FILE_NAMES), SKIPPED_PATH.pattern))
    digest = hashlib.sha256(rules.encode())
    return digest.hexdigest()[:12]


RULES_FINGERPRINT = fingerprint_rules()


def count_lines(github: GitHub, repository: str, sha: str) -> LineCount:
    files, stats = changed_files(github, repository, sha)
    if not files and stats.get("total"):
        return estimate_from_stats(stats)

    code_files = [changed_file for changed_file in files if is_code(changed_file["filename"])]
    added = sum(changed_file["additions"] for changed_file in code_files)
    removed = sum(changed_file["deletions"] for changed_file in code_files)
    return LineCount(added, removed)


def changed_files(github: GitHub, repository: str, sha: str) -> tuple[list[dict], dict]:
    files = []
    stats = {}
    page_number = 1

    while True:
        commit = github.get(f"/repos/{repository}/commits/{sha}?per_page={FILES_PER_PAGE}&page={page_number}")
        commit = commit or {}
        stats = stats or commit.get("stats", {})
        page_files = commit.get("files", [])
        files.extend(page_files)

        if len(page_files) < FILES_PER_PAGE:
            return files, stats
        page_number += 1


def estimate_from_stats(stats: dict) -> LineCount:
    return LineCount(stats["additions"], stats["deletions"], exact=False)


def is_code(path: str) -> bool:
    file = PurePosixPath(path)
    if file.name in SKIPPED_FILE_NAMES or SKIPPED_PATH.search(path):
        return False

    return file.suffix.lower() in CODE_EXTENSIONS
