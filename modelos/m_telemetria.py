from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from db.conn import Base

class Telemetria(Base):
    __tablename__ = "telemetria"

    id = Column(Integer, primary_key=True, index=True)
    ConnectionDeviceId = Column(String)
    EventProcessedUtcTime = Column(String)
    HEFESTO_ID = Column(String)
    timestamp = Column(DateTime)
    var_name = Column(String)
    value = Column(Integer)
    plugin = Column(String)
    request = Column(String)
    var_name_1 = Column(String)
    device = Column(Integer)