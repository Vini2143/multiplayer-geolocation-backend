import re
from typing import Annotated, TypeVar
from pydantic import AfterValidator, BaseModel, ConfigDict

class OrmBaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, regex_engine="python-re")
