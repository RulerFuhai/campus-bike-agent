# app/models.py
from sqlalchemy import Column, Integer, String
from .database import Base

class VehicleInfo(Base):
    __tablename__ = "vehicle_info"   # 与你的表名保持一致

    id = Column(Integer, primary_key=True, index=True)
    license = Column(String(64), unique=True, index=True)        # 原来的 bike_id → license
    Brand = Column(String(32))                                   # 注意大小写要和 Excel 列名对应
    color = Column(String(32))
    original_location = Column(String(255))
    current_location = Column(String(255))                       # 原来的 new_location → current_location
    attachment = Column(String(255))
    other_feature = Column(String(255))
