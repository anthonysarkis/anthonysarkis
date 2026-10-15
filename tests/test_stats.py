from datetime import date, datetime

from harvest.commits import Commit
from harvest.stats import Age, age, is_night, longest_streak, summarize

BORN = date(2000, 7, 28)


class TestAge:
    def test_years_months_and_days(self):
        assert age(BORN, date(2026, 10, 15)) == Age(26, 2, 17)

    def test_on_the_birthday(self):
        assert age(BORN, date(2026, 7, 28)) == Age(26, 0, 0)

    def test_the_day_before_the_birthday(self):
        assert age(BORN, date(2026, 7, 27)) == Age(25, 11, 29)

    def test_born_on_the_31st_after_a_short_month(self):
        assert age(date(2000, 1, 31), date(2000, 3, 1)) == Age(0, 1, 1)


class TestLongestStreak:
    def test_counts_consecutive_days(self):
        days = [date(2026, 1, 1), date(2026, 1, 2), date(2026, 1, 3), date(2026, 1, 5)]
        assert longest_streak(days) == 3

    def test_one_day_is_a_streak_of_one(self):
        assert longest_streak([date(2026, 1, 1)]) == 1


class TestIsNight:
    def test_from_ten_pm_to_five_am(self):
        assert is_night(datetime(2026, 1, 1, 22))
        assert is_night(datetime(2026, 1, 1, 4, 59))

    def test_daytime(self):
        assert not is_night(datetime(2026, 1, 1, 5))
        assert not is_night(datetime(2026, 1, 1, 21, 59))


class TestSummarize:
    def test_adds_up_the_commits(self):
        commits = [
            Commit("me/farm", datetime(2026, 3, 1, 23), 10, 2),
            Commit("me/farm", datetime(2026, 3, 2, 12), 5, 1),
            Commit("me/cow", datetime(2025, 6, 1, 12), 7, 0),
        ]
        harvest = summarize(commits, date(2026, 10, 15), BORN, "6:22 am")

        assert harvest.lines_added == 22
        assert harvest.lines_removed == 3
        assert harvest.repositories == 2
        assert harvest.commits == 3
        assert harvest.commits_this_year == 2
        assert harvest.longest_streak == 2
        assert harvest.night_percent == 33
        assert harvest.bedtime == "6:22 am"
