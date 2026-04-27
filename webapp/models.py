import uuid
import datetime
from sqlalchemy import Column, String, Boolean, Float, DateTime
from .db import Base

class Switch(Base):
    __tablename__ = "switches"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, index=True)
    is_on = Column(Boolean, default=False)
    total_time_seconds = Column(Float, default=0.0)
    last_turned_on = Column(DateTime, nullable=True)
