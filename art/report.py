from harvest.stats import Harvest

from .terminal import GREEN, RED, WHITE, Row

HEADER = "🌾 Harvest report"
MINUS_SIGN = "\N{MINUS SIGN}"


def report_rows(harvest: Harvest) -> list[Row]:
    years, months, days = harvest.age
    uptime = f"{plural(years, 'year')}, {plural(months, 'month')}, {plural(days, 'day')}"
    packages = f"{plural(harvest.repositories, 'repo')}, {plural(harvest.commits, 'commit')}"
    streak = f"{plural(harvest.longest_streak, 'day')} in a row"
    season = f"{plural(harvest.commits_this_year, 'commit')} so far"

    return [
        Row("💻 OS", [(f"Anthony v{years}.{months}.{days} LTS", WHITE)]),
        Row("🏡 Host", [("📍 Montréal, QC", WHITE)]),
        Row("🎂 Uptime", [(uptime, WHITE)]),
        Row("🌱 Lines planted", [(f"+{harvest.lines_added:,}", GREEN)]),
        Row("🌿 Weeds pulled", [(f"{MINUS_SIGN}{harvest.lines_removed:,}", RED), (" lines deleted", WHITE)]),
        Row("📦 Packages", [(packages, WHITE)]),
        Row("🔥 Longest streak", [(streak, WHITE)]),
        Row("🌙 Night shifts", [(f"{harvest.night_percent}% of commits after 10 pm", WHITE)]),
        Row("😴 Bedtime", [(harvest.bedtime, WHITE)]),
        Row(f"🚜 Season {harvest.day.year}", [(season, WHITE)]),
    ]


def report_label(harvest: Harvest) -> str:
    commits = plural(harvest.commits, "commit")
    repositories = plural(harvest.repositories, "repo")
    return (
        f"Harvest report: {harvest.lines_added:,} lines planted, {harvest.lines_removed:,} weeds pulled, "
        f"{commits} in {repositories}."
    )


def plural(count: int, word: str) -> str:
    return f"{count:,} {word}" if count == 1 else f"{count:,} {word}s"
