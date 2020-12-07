import csv
import json
from typing import Any, Optional, AnyStr, IO, Union, Tuple
import random
from random import choice, choices, uniform, randint

from faker import Faker


class MetaFaker:
    def __init__(self, meta: dict, **kwargs):
        """
        Creates an object that can generate fake data (using faker)
        based on the information provided via the input metadata.
        """
        self.columns = meta["columns"]
        self.special_cols = kwargs.get("special_cols", {})
        self.fake = Faker()
        self.default_min = kwargs.get("default_min", -1000)
        self.default_max = kwargs.get("default_max", 1000)
        self.null_probability = kwargs.get("null_probability", 0.1)
        self._seed = None

    @property
    def seed(self):
        return self._seed

    @seed.setter
    def seed(self, value):
        self._seed = value
        self.fake.seed_instance(value)
        random.seed(value)


    def null_column_value(self, col: dict) -> bool:
        """
        If meta data column is nullable (assumed False if unspecified). 
        Then will return True within the value based on the null_probability otherwise False
        """

        nullable = col.get("nullable", False)
        would_be_null = choices(
            [True, False],
            weights=[self.null_probability, 1 - self.null_probability],
            k=1,
        )[0]
        return nullable and would_be_null

    def generate_col_data(self, col: dict) -> Any:
        """
        Generate data based on the column properties
        """
        if self.null_column_value(col):
            return None

        elif col.get("enum"):
            return self.fake_enum(col.get("enum"))

        elif col["type"] in ["int", "long"]:
            return self.fake_int(col)

        elif col["type"] in ["double", "float"]:
            return self.fake_double(col)

        elif col["type"] in ["date", "datetime"]:
            return self.fake_datetime(col)

        elif col["type"] == "boolean":
            return self.fake_bool()

        elif col["type"] == "character":
            return self.fake_character(special_type=self.special_cols.get(col["name"]))
        else:
            n = col["name"]
            t = col["type"]
            raise TypeError(f"Column: {n} has unsupported type: {t}")

    def fake_int(self, col: dict) -> int:
        minimum, maximum = self.get_min_max(col)
        value = self.fake.random_int(min=minimum, max=maximum)
        return value

    def fake_double(self, col: dict) -> float:
        minimum, maximum = self.get_min_max(col)
        value = uniform(minimum, maximum)
        return value

    def get_min_max(self, col) -> Tuple[int, int]:
        """
        Sets default min max values
        """
        minimum = col.get("minimum", self.default_min)
        maximum = col.get("maximum", self.default_max)
        return (minimum, maximum)

    def fake_character(self, special_type: Optional[str] = None) -> str:
        """
        By default uses faker to return 1 - 10 random words with normal spacing.
        If special_type is given then the special type of faker property is called.
        E.g. if special_type = 'email' then the function would return fake.email().
        """
        if special_type:
            value = getattr(self.fake, special_type)()
        else:
            value = " ".join(self.fake.words(randint(1, 10)))
        return value

    def fake_datetime(self, col: dict) -> str:
        """
        Uses faker to create a fake date or date time string.
        If col input has a format key then that  format is used.
        Otherwise output will be ISO standard.
        """
        if self.null_column_value(col):
            return None
        else:
            date_format = col.get("format")
            if not date_format:
                if col["type"] == "date":
                    date_format = "%Y-%m-%d"
                else:
                    date_format = "%Y-%m-%d %H:%M:%S"

            value = self.fake.date(pattern=date_format)
            return value

    def fake_enum(self, enum: list) -> Any:
        """
        Randomly returns one of the values in list
        """
        return choice(enum)

    def fake_bool(self) -> bool:
        """
        Randomly returns True or False
        """
        return choice([True, False])

    def generate_row(self) -> dict:
        """
        Returns a dictionary of row name (key) -> value bindings.
        """
        row = {}
        for c in self.columns:
            row[c["name"]] = self.generate_col_data(c)
        return row

    def write_data_to_csv(
        self,
        filepath: Union[str, IO[AnyStr]],
        total_rows: int,
        delimiter: str = ",",
        header: bool = True,
    ):
        """
        Writes the fake data to a jsonl file. Note that total_rows does not include the header.
        Will write header if parameter is True (default).
        """
        local_file = isinstance(filepath, str)

        if local_file:
            f = open(filepath, "w")
        else:
            f = filepath

        writer = csv.DictWriter(
            f, fieldnames=[c["name"] for c in self.columns], delimiter=delimiter
        )
        if header:
            writer.writeheader()

        for i in range(total_rows):
            writer.writerow(self.generate_row())

        if local_file:
            f.close()

    def write_data_to_jsonl(self, filepath: Union[str, IO[AnyStr]], total_rows: int):
        """
        Writes the fake data to a jsonl file.
        """
        local_file = isinstance(filepath, str)

        if local_file:
            f = open(filepath, "w")
        else:
            f = filepath

        for i in range(total_rows):
            json.dump(self.generate_row(), f)
            f.write("\n")

        if local_file:
            f.close()
