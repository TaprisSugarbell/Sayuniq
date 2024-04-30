from typing import Any

import yaml
from decouple import config

try:
    from yaml import CDumper as Dumper
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Dumper, Loader  # noqa: F401


LANGUAGE = config("LANGUAGE", default="es")


def get_string(key: str) -> Any:
    stream = open(f"locales/{LANGUAGE}.yml", "rb")
    data = yaml.load(stream, Loader=Loader)
    return data[key]
