from datetime import date, datetime

from art.farm import farm_svg
from harvest.commits import Commit
from harvest.stats import summarize


class TestFarmSvg:
    def test_draws_the_harvest_numbers(self):
        commits = [
            Commit("me/farm", datetime(2026, 10, 14, 23), 1234, 56),
            Commit("me/cow", datetime(2026, 10, 15, 9), 10, 0),
        ]
        harvest = summarize(commits, date(2026, 10, 15), date(2000, 7, 28), "6:22 am")

        picture = farm_svg(harvest)

        assert picture.startswith("<svg ")
        assert picture.endswith("</svg>\n")
        assert "+1,244" in picture
        assert "\N{MINUS SIGN}56" in picture
        assert "2 repos, 2 commits" in picture
        assert "6:22 am" in picture
