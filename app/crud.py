# app/crud.py
from sqlalchemy.orm import Session
from . import models, schemas

def query_vehicle_info(
    db: Session,
    original_location: str,
    color: str,
    license: str = None,
    Brand: str = None,
    attachment: str = None,
    other_feature: str = None,
):
    q = db.query(models.VehicleInfo)
    # 必填项
    q = q.filter(models.VehicleInfo.original_location == original_location)
    q = q.filter(models.VehicleInfo.color == color)
    # 选填项
    if license:
        q = q.filter(models.VehicleInfo.license == license)
    if Brand:
        q = q.filter(models.VehicleInfo.Brand == Brand)
    if attachment:
        q = q.filter(models.VehicleInfo.attachment == attachment)
    if other_feature:
        q = q.filter(models.VehicleInfo.other_feature == other_feature)
    return q.all()
