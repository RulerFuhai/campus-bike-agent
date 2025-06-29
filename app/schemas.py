# app/schemas.py
from pydantic import BaseModel
from typing import List

class VehicleInfoBase(BaseModel):
    license: str
    Brand: str
    color: str
    original_location: str
    current_location: str
    attachment: str
    other_feature: str

class VehicleInfoCreate(VehicleInfoBase):
    pass

class VehicleInfoOut(VehicleInfoBase):
    id: int

    class Config:
        # Pydantic V2 ORM 模式配置
        from_attributes = True

class VehicleInfoList(BaseModel):
    items: List[VehicleInfoOut]
