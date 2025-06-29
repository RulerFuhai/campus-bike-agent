# app/crud.py
from sqlalchemy.orm import Session
from . import models, schemas

def create_vehicle_info(db: Session, info: schemas.VehicleInfoCreate):
    """
    创建一条新的 VehicleInfo 记录，并返回该对象。
    """
    db_obj = models.VehicleInfo(**info.dict())
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
    """
    按条件查询 VehicleInfo 记录，并返回 Pydantic 模型列表。
    """
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

    # 执行查询并将 ORM 对象转换为 Pydantic
    items = q.all()
    return [schemas.VehicleInfoOut.from_orm(item) for item in items]
