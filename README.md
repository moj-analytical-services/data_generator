# data_generator

![unit-tests.yml](https://github.com/moj-analytical-services/data_generator/workflows/unit-tests.yml/badge.svg)

Generates data using faker and our meta data schemas. This package expects meta data that conforms to the ETL Manager schema [repo here](https://github.com/moj-analytical-services/etl_manager)

```python

from data_generator.data_generator import MetaFaker

meta = {
    "columns": [
        {
            "name": "my_int",
            "type": "int",
            "minimum": 10,
            "maximum": 20,
            "nullable": True
        },
        {
            "name": "my_character_enum",
            "type": "character",
            "enum": ["a", "b", "c"]
        },
        {
            "name": "my_email",
            "type": "character",
        },
        {
            "name": "my_datetime",
            "type": "datetime",
        }
    ]
}

sc = {
    "my_email": "email",
}

mf = MetaFaker(meta=meta, special_cols=sc)
mf.generate_row()
```

Would return something like this:

```
{
    'my_int': 18,
    'my_character_enum': 'a',
    'my_email': 'powerssarah@sanders-hill.info',
    'my_datetime': '1988-05-24 10:00:57',
}
```

Can also write to jsonl or csv

```python
#csv
mf.write_data_to_csv("test.csv", total_rows=10)

# jsonl 
mf.write_data_to_jsonl("test.jsonl", 10)
```

## Special Case Characters

In the above example you could see that we stated that the my_email column should produce email-like strings in the following way.

```python
...
sc = {
    "my_email": "email",
}
...
```

The sc parameter works for the key/value pair where the key is the column name (in the data to be generated) and the value is a string that is the name of the provider in the Faker package that is called under the hood of this package [(this line shows how).](data_generator/data_generator.py#L103). To find what other types of specific strings you can generate e.g. address, name, last_name, etc. Please look at [Faker providers](https://faker.readthedocs.io/en/stable/providers/baseprovider.html).
