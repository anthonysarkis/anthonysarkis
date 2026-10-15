import http.client
import urllib.error

import pytest

from harvest.github import GitHub


def fail_to_connect(url: str) -> None:
    raise urllib.error.URLError("connection refused")


class DroppedOnce:
    def __init__(self) -> None:
        self.dropped = False

    def send(self, url: str) -> tuple[dict, dict]:
        if not self.dropped:
            self.dropped = True
            raise http.client.RemoteDisconnected("Remote end closed connection without response")

        return {"login": "anthonysarkis"}, {}


class TestRequest:
    def test_retries_when_github_drops_the_connection(self, monkeypatch):
        github = GitHub("token")
        connection = DroppedOnce()
        waits = []
        monkeypatch.setattr(github, "send", connection.send)
        monkeypatch.setattr("harvest.github.time.sleep", waits.append)

        user = github.get("/user")

        assert user == {"login": "anthonysarkis"}

    def test_the_failure_message_never_names_the_repository(self, monkeypatch):
        github = GitHub("token")
        waits = []
        monkeypatch.setattr(github, "send", fail_to_connect)
        monkeypatch.setattr("harvest.github.time.sleep", waits.append)

        with pytest.raises(RuntimeError) as failure:
            github.get("/repos/secret-org/private-repo/commits/abc1234")

        assert "private-repo" not in str(failure.value)
