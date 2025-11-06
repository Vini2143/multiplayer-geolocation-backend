from typing import Dict
from pydantic import AfterValidator, BaseModel, ConfigDict

class WsEventSchema(BaseModel):
    event_type: str
    data: Dict
