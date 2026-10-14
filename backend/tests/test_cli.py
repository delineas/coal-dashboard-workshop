import pytest

from app import cli, etl
from tests.test_etl import FIXTURES


@pytest.fixture
def db_path(tmp_path):
    path = tmp_path / "coal.sqlite"
    etl.build(FIXTURES / "units_2017.csv", FIXTURES / "units_2023.csv", path)
    return path


def test_schema_lists_views_with_columns(db_path, capsys):
    cli.main(["schema"], db_path)
    assert "country_capacity(name, mw_2017, mw_2023, cmp_2017, cmp_2023, delta_mw, coverage_mw, pct_change, trend)" in capsys.readouterr().out


def test_sql_prints_tab_separated_rows(db_path, capsys):
    cli.main(["sql", "SELECT name, mw_2017 FROM country_capacity ORDER BY name"], db_path)
    assert capsys.readouterr().out.splitlines()[:2] == ["name\tmw_2017", "Atlantis\t540.0"]


def test_sql_marks_truncated_output(db_path, capsys):
    cli.main(["sql", "SELECT tracker_id FROM units", "--limit", "1"], db_path)
    assert capsys.readouterr().out.splitlines()[-1] == "... more than 1 rows"


def test_sql_cannot_write(db_path):
    with pytest.raises(SystemExit, match="readonly"):
        cli.main(["sql", "DELETE FROM units"], db_path)
