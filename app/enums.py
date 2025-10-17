from enum import Enum


class SomeEnum(str, Enum):
    property_a = "property_a"
    property_b = "property_b"


class OtherEnum(int, Enum):
    value_a = 1
    value_b = 2