import pytest

from harvest.lines import LineCount, count_lines, is_code


class FakeGitHub:
    def __init__(self, commit: dict) -> None:
        self.commit = commit

    def get(self, path: str) -> dict:
        return self.commit


class TestIsCode:
    @pytest.mark.parametrize("path", ["src/app.ts", "analysis/model.R", "scripts/deploy.sh", "db/schema.sql"])
    def test_code_files(self, path):
        assert is_code(path)

    @pytest.mark.parametrize(
        "path",
        [
            "README.md",
            "package-lock.json",
            "web/node_modules/react/index.js",
            "dist/bundle.js",
            "static/app.min.js",
            "api/schema.generated.ts",
        ],
    )
    def test_files_nobody_types(self, path):
        assert not is_code(path)


class TestCountLines:
    def test_only_code_files_count(self):
        commit = {
            "stats": {"total": 60, "additions": 50, "deletions": 10},
            "files": [
                {"filename": "app.py", "additions": 20, "deletions": 5},
                {"filename": "package-lock.json", "additions": 30, "deletions": 5},
            ],
        }
        assert count_lines(FakeGitHub(commit), "me/farm", "abc") == LineCount(20, 5)

    def test_estimates_from_stats_when_github_lists_no_files(self):
        commit = {"stats": {"total": 60, "additions": 50, "deletions": 10}, "files": []}
        assert count_lines(FakeGitHub(commit), "me/farm", "abc") == LineCount(50, 10, exact=False)

    def test_empty_commit(self):
        commit = {"stats": {"total": 0, "additions": 0, "deletions": 0}, "files": []}
        assert count_lines(FakeGitHub(commit), "me/farm", "abc") == LineCount(0, 0)
