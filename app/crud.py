from sqlalchemy.orm import Session
from app.models import VehicleInfo, LicenseBinding
from app.schemas import VehicleInfoCreate, LicenseBindingCreate

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

# —— 绑定和查询邮箱 ——
def bind_license_email(db: Session, info: LicenseBindingCreate):
    obj = db.query(LicenseBinding).filter(LicenseBinding.license == info.license).first()
    if obj:
        obj.email = info.email
    else:
        obj = LicenseBinding(license=info.license, email=info.email)
        db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def get_binding(db: Session, license: str):
    return db.query(LicenseBinding).filter(LicenseBinding.license == license).first()
