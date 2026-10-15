import http.client
import json
import re
import sys
import time
import urllib.error
import urllib.request
from http import HTTPStatus

API = "https://api.github.com"
ATTEMPTS = 6
LONGEST_WAIT_SECONDS = 3600
EMPTY_REPOSITORY = HTTPStatus.CONFLICT
NETWORK_ERRORS = (OSError, http.client.HTTPException)
NEXT_PAGE_LINK = re.compile(r'<([^>]+)>;\s*rel="next"')


class GitHub:
    def __init__(self, token: str) -> None:
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def get(self, path: str) -> object:
        body, _ = self.request(API + path)
        return body

    def get_all_pages(self, path: str) -> list:
        items = []
        url = API + path

        while url:
            page, headers = self.request(url)
            if page is None:
                break

            items.extend(page)
            url = next_page_url(headers)

        return items

    def request(self, url: str) -> tuple[object, dict]:
        for attempt in range(ATTEMPTS):
            try:
                return self.send(url)
            except urllib.error.HTTPError as error:
                if error.code == EMPTY_REPOSITORY:
                    return None, {}
                wait_before_retry(error, attempt)
            except NETWORK_ERRORS:
                time.sleep(2**attempt)

        raise RuntimeError(f"GitHub kept failing after {ATTEMPTS} attempts")

    def send(self, url: str) -> tuple[object, dict]:
        api_request = urllib.request.Request(url, headers=self.headers)
        with urllib.request.urlopen(api_request, timeout=60) as response:
            body = response.read()
            headers = dict(response.headers)

        data = json.loads(body) if body else None
        return data, headers


def next_page_url(headers: dict) -> str | None:
    link = NEXT_PAGE_LINK.search(headers.get("Link", ""))
    return link.group(1) if link else None


def wait_before_retry(error: urllib.error.HTTPError, attempt: int) -> None:
    rate_limit_seconds = rate_limit_wait(error)

    if rate_limit_seconds is not None:
        print(f"Rate limited, waiting {rate_limit_seconds}s", file=sys.stderr)
        time.sleep(rate_limit_seconds)
    elif error.code >= HTTPStatus.INTERNAL_SERVER_ERROR:
        time.sleep(2**attempt)
    else:
        raise error


def rate_limit_wait(error: urllib.error.HTTPError) -> int | None:
    retry_after = error.headers.get("Retry-After")
    out_of_calls = error.headers.get("X-RateLimit-Remaining") == "0"
    forbidden_by_limit = error.code == HTTPStatus.FORBIDDEN and (retry_after or out_of_calls)
    if error.code != HTTPStatus.TOO_MANY_REQUESTS and not forbidden_by_limit:
        return None

    if retry_after:
        return min(int(retry_after), LONGEST_WAIT_SECONDS)

    reset_at = int(error.headers.get("X-RateLimit-Reset") or 0)
    seconds_until_reset = max(reset_at - int(time.time()), 0) + 5
    return min(seconds_until_reset, LONGEST_WAIT_SECONDS)
