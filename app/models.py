# app/models.py
from sqlalchemy import Column, Integer, String
from .database import Base

class VehicleInfo(Base):
    __tablename__ = "vehicle_info"

    id = Column(Integer, primary_key=True, index=True)
    # 去掉 unique=True，让多个 "无" 也能插入
    license = Column(String(64), index=True)
    Brand = Column(String(32))
    color = Column(String(32))
    original_location = Column(String(255))
    current_location = Column(String(255))
    attachment = Column(String(255))
    other_feature = Column(String(255))
