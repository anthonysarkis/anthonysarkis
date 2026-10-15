import urllib.error

import pytest

from harvest.github import GitHub


def fail_to_connect(url: str) -> None:
    raise urllib.error.URLError("connection refused")


class TestRequest:
    def test_the_failure_message_never_names_the_repository(self, monkeypatch):
        github = GitHub("token")
        monkeypatch.setattr(github, "send", fail_to_connect)
        monkeypatch.setattr("harvest.github.time.sleep", lambda seconds: None)

        with pytest.raises(RuntimeError) as failure:
            github.get("/repos/secret-org/private-repo/commits/abc1234")

        assert "private-repo" not in str(failure.value)
