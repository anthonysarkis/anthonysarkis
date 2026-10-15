from art.terminal import BLANK_LINE, WHITE, Row, Section, report_lines

CROPS = Section("Crops", [Row("Corn", [("12 rows", WHITE)])])
FARMER = Section("Farmer", [Row("Host", [("Montréal", WHITE)])])


class TestReportLines:
    def test_each_section_has_a_title_a_rule_and_its_rows(self):
        lines = report_lines([CROPS])

        assert len(lines) == 3
        assert "Crops" in lines[0]
        assert "─────" in lines[1]
        assert "12 rows" in lines[2]

    def test_a_blank_line_separates_sections(self):
        lines = report_lines([CROPS, FARMER])

        assert len(lines) == 7
        assert lines[3] == BLANK_LINE
        assert "Farmer" in lines[4]
