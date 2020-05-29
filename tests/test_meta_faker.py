import pytest

from data_generator.data_generator import MetaFaker
from io import StringIO

from datetime import datetime


def test_readme():

    meta = {
        "columns": [
            {
                "name": "my_int",
                "type": "int",
                "minimum": 10,
                "maximum": 20,
                "nullable": True,
            },
            {"name": "my_character_enum", "type": "character", "enum": ["a", "b", "c"]},
            {"name": "my_email", "type": "character",},
            {"name": "my_datetime", "type": "datetime",},
        ]
    }

    sc = {"my_email": "email"}
    mf = MetaFaker(meta=meta, special_cols=sc)
    row = mf.generate_row()

    #  Make checks against row
    assert row["my_int"] >= 10 or row["my_int"] is None
    assert row["my_int"] <= 20 or row["my_int"] is None

    assert row["my_character_enum"] in ["a", "b", "c"]

    assert "@" in row["my_email"]

    # Check for no errors
    dt = datetime.strptime(row["my_datetime"], "%Y-%m-%d %H:%M:%S")
    mf.write_data_to_csv(StringIO(), total_rows=10)
    mf.write_data_to_jsonl(StringIO(), 10)


def test_nulling():
    meta = {
        "columns": [
            {"name": "my_int", "type": "int", "nullable": True},
            {"name": "my_character", "type": "character", "nullable": True},
        ]
    }
    mf = MetaFaker(meta=meta, null_probability=1.0)
    row = mf.generate_row()
    for k, v in row.items():
        assert v is None


def test_character():

    pontiless_meta = {"columns": [{"name": "test", "type": "character"}]}
    mf = MetaFaker(pontiless_meta)
    assert isinstance(mf.fake_character(), str)

    assert isinstance(mf.fake_character("email"), str)
    assert "@" in mf.fake_character("email")

    assert isinstance(mf.fake_character("address"), str)
    assert isinstance(mf.fake_character("street_address"), str)
    assert isinstance(mf.fake_character("first_name"), str)
    assert isinstance(mf.fake_character("first_name_female"), str)
    assert isinstance(mf.fake_character("first_name_male"), str)

    # Check row generator
    row = mf.generate_row()
    assert isinstance(row["test"], str)

    # Check special rows work
    mf.special_cols = {"test": "email"}
    row = mf.generate_row()
    assert "@" in row["test"]


def test_int():

    col = {"name": "test", "type": "int"}
    pontiless_meta = {"columns": [col]}
    mf = MetaFaker(pontiless_meta)
    test_int = mf.fake_int(col)
    assert isinstance(test_int, int)
    assert test_int >= mf.default_min and test_int <= mf.default_max

    # Check row generator
    row = mf.generate_row()
    assert isinstance(row["test"], int)
    assert row["test"] >= mf.default_min and row["test"] <= mf.default_max

    # Check limits work
    meta = {"columns": [{"name": "test", "type": "int", "minimum": 0, "maximum": 2}]}
    mf = MetaFaker(meta)
    row = mf.generate_row()
    assert isinstance(row["test"], int)
    assert row["test"] in [0, 1, 2]


@pytest.mark.parametrize("t", ["float", "double"])
def test_number(t):

    col = {"name": "test", "type": t}
    pontiless_meta = {"columns": [col]}
    mf = MetaFaker(pontiless_meta)
    test_double = mf.fake_double(col)
    assert isinstance(test_double, float)
    assert test_double >= mf.default_min and test_double <= mf.default_max

    # Check row generator
    row = mf.generate_row()
    assert isinstance(row["test"], float)
    assert row["test"] >= mf.default_min and row["test"] <= mf.default_max

    # Check limits work
    meta = {"columns": [{"name": "test", "type": t, "minimum": 0, "maximum": 2}]}
    mf = MetaFaker(meta)
    row = mf.generate_row()
    assert isinstance(row["test"], float)
    assert row["test"] >= 0.0
    assert row["test"] <= 2.0


def test_bool():
    col = {"name": "test", "type": "boolean"}
    pontiless_meta = {"columns": [col]}
    mf = MetaFaker(pontiless_meta)
    test_bool = mf.fake_bool()
    assert isinstance(test_bool, bool)
    assert test_bool in [True, False]

    # Check row generator
    row = mf.generate_row()
    assert isinstance(row["test"], bool)


@pytest.mark.parametrize(
    "col,exp_fmt",
    [
        ({"name": "test", "type": "datetime"}, "%Y-%m-%d %H:%M:%S"),
        ({"name": "test", "type": "date"}, "%Y-%m-%d"),
        ({"name": "test", "type": "date", "format": "%d/%m/%Y"}, "%d/%m/%Y"),
    ],
)
def test_dates(col, exp_fmt):

    meta = {"columns": [col]}
    mf = MetaFaker(meta)

    # Check datetime creation
    test_date = mf.fake_datetime(col)
    assert isinstance(test_date, str)
    datetime.strptime(test_date, exp_fmt)

    # Check row generator
    row = mf.generate_row()
    assert isinstance(row["test"], str)
    datetime.strptime(row["test"], exp_fmt)
