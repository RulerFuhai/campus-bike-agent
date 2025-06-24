# app/crud.py
from sqlalchemy.orm import Session
from . import models, schemas

def create_vehicle_info(db: Session, data: schemas.VehicleInfoCreate):
    db_obj = models.VehicleInfo(**data.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def query_vehicle_info(db: Session, license: str = None):
    q = db.query(models.VehicleInfo)
    if license:
        q = q.filter(models.VehicleInfo.license == license)
    return q.all()
