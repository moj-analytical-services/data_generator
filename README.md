# data_generator
Generates data using faker and our meta data schemas


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
