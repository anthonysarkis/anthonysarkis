import json

from harvest.counted_commits import load_counts, save_counts
from harvest.lines import LineCount


class TestCountedCommits:
    def test_saved_counts_load_back(self, tmp_path):
        path = tmp_path / "counted-commits.json"
        counts = {"bbb": LineCount(3, 4), "aaa": LineCount(10, 0)}

        save_counts(path, counts)

        assert load_counts(path) == counts

    def test_the_file_is_valid_json_sorted_by_sha(self, tmp_path):
        path = tmp_path / "counted-commits.json"

        save_counts(path, {"bbb": LineCount(3, 4), "aaa": LineCount(10, 0)})

        saved = json.loads(path.read_text())
        assert list(saved["commits"]) == ["aaa", "bbb"]

    def test_a_missing_file_has_no_counts(self, tmp_path):
        assert load_counts(tmp_path / "missing.json") == {}

    def test_counts_made_under_other_rules_are_dropped(self, tmp_path):
        path = tmp_path / "counted-commits.json"
        path.write_text('{"rules": "older", "commits": {"aaa": [1, 2]}}')

        assert load_counts(path) == {}
