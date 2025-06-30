# app/crud.py
from sqlalchemy.orm import Session
from models import VehicleInfo
from schemas import VehicleInfoCreate

def create_vehicle_info(db: Session, info: VehicleInfoCreate):
    db_obj = VehicleInfo(
        license=info.license,
        Brand=info.Brand,
        color=info.color,
        original_location=info.original_location,
        current_location=info.current_location,
        attachment=info.attachment,
        other_feature=info.other_feature,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def query_vehicle_info(
    db: Session,
    original_location: str,
    color: str,
    license: str = None,
    Brand: str = None,
    attachment: str = None,
    other_feature: str = None,
):
    q = db.query(VehicleInfo).filter(
        VehicleInfo.original_location == original_location,
        VehicleInfo.color == color,
    )
    if license:
        q = q.filter(VehicleInfo.license == license)
    if Brand:
        q = q.filter(VehicleInfo.Brand == Brand)
    if attachment:
        q = q.filter(VehicleInfo.attachment == attachment)
    if other_feature:
        q = q.filter(VehicleInfo.other_feature == other_feature)
    return q.all()

def get_all_vehicles(db: Session):
    return db.query(VehicleInfo).all()

def delete_vehicle_by_id(db: Session, vehicle_id: int) -> bool:
    obj = db.query(VehicleInfo).filter(VehicleInfo.id == vehicle_id).first()
    if obj:
        db.delete(obj)
        db.commit()
        return True
    return False

def clear_all_vehicles(db: Session) -> int:
    count = db.query(VehicleInfo).delete()
    db.commit()
    return count
