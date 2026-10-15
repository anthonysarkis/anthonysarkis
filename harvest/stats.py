import calendar
from collections import Counter
from collections.abc import Iterable
from datetime import date, datetime
from itertools import pairwise
from typing import NamedTuple

from .commits import Commit

NIGHT_START_HOUR = 22
NIGHT_END_HOUR = 5


class Age(NamedTuple):
    years: int
    months: int
    days: int


class Harvest(NamedTuple):
    day: date
    age: Age
    lines_added: int
    lines_removed: int
    repositories: int
    commits: int
    commits_by_day: Counter[date]
    commits_this_year: int
    longest_streak: int
    night_percent: int
    bedtime: str


def summarize(commits: list[Commit], today: date, born: date, bedtime: str) -> Harvest:
    commits_by_day = Counter(commit.local_time.date() for commit in commits)
    night_commits = sum(is_night(commit.local_time) for commit in commits)
    commits_this_year = sum(commit.local_time.year == today.year for commit in commits)

    return Harvest(
        day=today,
        age=age(born, today),
        lines_added=sum(commit.lines_added for commit in commits),
        lines_removed=sum(commit.lines_removed for commit in commits),
        repositories=len({commit.repository for commit in commits}),
        commits=len(commits),
        commits_by_day=commits_by_day,
        commits_this_year=commits_this_year,
        longest_streak=longest_streak(commits_by_day.keys()),
        night_percent=round(100 * night_commits / len(commits)),
        bedtime=bedtime,
    )


def age(born: date, on: date) -> Age:
    before_birthday = (on.month, on.day) < (born.month, born.day)
    before_monthly_birthday = on.day < born.day

    years = on.year - born.year - before_birthday
    months = (on.month - born.month - before_monthly_birthday) % 12
    days = (on - last_monthly_birthday(born, on)).days
    return Age(years, months, days)


def last_monthly_birthday(born: date, on: date) -> date:
    year, month = on.year, on.month
    if on.day < born.day:
        year, month = (year - 1, 12) if month == 1 else (year, month - 1)

    _, days_in_month = calendar.monthrange(year, month)
    return date(year, month, min(born.day, days_in_month))


def longest_streak(active_days: Iterable[date]) -> int:
    days = sorted(active_days)
    longest = current = 1

    for previous_day, day in pairwise(days):
        current = current + 1 if (day - previous_day).days == 1 else 1
        longest = max(longest, current)

    return longest


def is_night(moment: datetime) -> bool:
    return moment.hour >= NIGHT_START_HOUR or moment.hour < NIGHT_END_HOUR
