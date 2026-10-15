from collections import Counter
from datetime import date

from art.field import plant_levels, shown_days

TODAY = date(2026, 10, 15)


class TestShownDays:
    def test_whole_weeks_from_sunday_a_year_ago_to_this_saturday(self):
        days = shown_days(TODAY)

        assert len(days) == 53 * 7
        assert days[0].weekday() == 6
        assert days[-1] == date(2026, 10, 17)


class TestPlantLevels:
    def test_busier_days_grow_taller_plants_by_quartile(self):
        days = shown_days(TODAY)
        commits_by_day = Counter({day: count for count, day in enumerate(days[:8], start=1)})

        levels = plant_levels(commits_by_day, days, TODAY)

        assert [levels[day] for day in days[:8]] == [1, 1, 1, 2, 2, 3, 3, 4]

    def test_days_without_commits_stay_bare(self):
        days = shown_days(TODAY)

        assert plant_levels(Counter(), days, TODAY) == {}
