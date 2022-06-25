import os
import yaml
from decouple import config
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
from typing import Any


LANGUAGE = config("LANGUAGE", default="es")


def get_string(key: str) -> Any:
    stream = open(f"./strings/{LANGUAGE}.yml", "rb")
    data = yaml.load(stream, Loader=Loader)
    return data[key]

