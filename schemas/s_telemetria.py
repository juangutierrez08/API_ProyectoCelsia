from pydantic import BaseModel
from datetime import datetime


class TelemetriaBase(BaseModel):
    ConnectionDeviceId : str
    EventProcessedUtcTime : str   
    HEFESTO_ID : str
    timestamp : datetime
    var_name : str
    value : int
    plugin : str
    request : str
    var_name_1 : str
    device : int

class TelemetriaCreate(TelemetriaBase):
    pass

class Telemetria(TelemetriaBase):
    id: int

    class Config:
        orm_mode = True