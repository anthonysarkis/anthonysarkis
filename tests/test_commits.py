from datetime import UTC, datetime

from harvest.commits import ListedCommit, count_new_commits

PRIVATE_REPOSITORY = "secret-org/private-repo"


class FakeGitHub:
    def get(self, path: str) -> dict:
        return {"stats": {"total": 12, "additions": 10, "deletions": 2}, "files": []}


class TestCountNewCommits:
    def test_the_log_never_names_the_repository(self, capsys):
        commit = ListedCommit(PRIVATE_REPOSITORY, "abc1234def5678", datetime(2026, 10, 15, tzinfo=UTC))

        count_new_commits(FakeGitHub(), [commit], saved_counts={})

        log = capsys.readouterr().err
        assert "abc1234" in log
        assert "private-repo" not in log
