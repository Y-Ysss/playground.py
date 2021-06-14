# https://github.com/Tinche/cattrs
# https://pypi.org/project/cattrs/

import json
from dataclasses import dataclass
from typing import Dict, Optional, Union

from cattr import register_structure_hook, structure


@dataclass
class Format:
    true: Optional[str] = None
    false: Optional[str] = None


@dataclass
class DataValue:
    key: str
    format: Dict[str, Format]


@dataclass
class Book:
    title: str
    year: str
    page: int


@dataclass
class Data:
    name: str
    books: Dict[str, Book]
    data: Dict[str, Union[DataValue, str]]


json_str = """
{
    "name": "Alice",
    "books": {
        "book1": {
            "title": "Python Beginners",
            "year": 2005,
            "page": 399
        },
        "book2": {
            "title": "Python Developers",
            "year": 2006,
            "page": 650
        }
    },
    "data":{
        "aa": "uiss",
        "bb": {
            "key": "k123",
            "format": {
                "true": "tt"
            }
        },
        "cc": "fa",
        "dd": {
            "key": "k456",
            "format": {
                "true": "t2",
                "false": "f2"
            }
        }
    }
}
"""

if __name__ == '__main__':
    d = json.loads(json_str)
    print(d)
    register_structure_hook(Union[DataValue, str], lambda o, _: structure(o, DataValue if isinstance(o, dict) else str))
    register_structure_hook(Dict[str, Format], lambda o, _: structure(o, Format))
    data = structure(d, Data)
    print(data)
