from sqlalchemy import Column, Integer, String
from .database import Base

class VehicleInfo(Base):
    __tablename__ = "vehicle_info"

    id = Column(Integer, primary_key=True, index=True)
    license = Column(String(64), index=True)
    Brand = Column(String(32))
    color = Column(String(32))
    original_location = Column(String(255))
    current_location = Column(String(255))
    attachment = Column(String(255))
    other_feature = Column(String(255))

class LicenseBinding(Base):
    __tablename__ = "license_binding"

    id = Column(Integer, primary_key=True, index=True)
    license = Column(String(64), unique=True, index=True)
    email = Column(String(128), index=True)
