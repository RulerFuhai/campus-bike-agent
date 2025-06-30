# app/schemas.py
from pydantic import BaseModel
from typing import List, Optional

class VehicleInfoBase(BaseModel):
    license: str
    Brand: str
    color: str
    original_location: str
    current_location: str
    attachment: Optional[str] = None
    other_feature: Optional[str] = None

class VehicleInfoCreate(VehicleInfoBase):
    pass

class VehicleInfoOut(VehicleInfoBase):
    id: int

    class Config:
        # Pydantic V2 ORM 模式
        from_attributes = True

class VehicleInfoList(BaseModel):
    items: List[VehicleInfoOut]

# ——— 管理员相关模型 ———
class AdminLoginRequest(BaseModel):
    password: str

class AdminLoginResponse(BaseModel):
    message: str
    menu: List[str]

class Message(BaseModel):
    message: str
