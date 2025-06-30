# app/main.py
import os
from typing import List

from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from . import crud, models, schemas
from .database import SessionLocal, engine

# 加载环境变量
load_dotenv()
API_KEY = os.getenv("PLUGIN_API_KEY")

# 创建所有表
models.Base.metadata.create_all(bind=engine)

# 实例化 FastAPI
app = FastAPI(title="Vehicle Info Plugin")

# 依赖：获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 依赖：简单的 API Key 验证
def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

# POST 路由：登记车辆信息
@app.post(
    "/vehicle/info",
    response_model=schemas.VehicleInfoOut,
    dependencies=[Depends(verify_api_key)]
)
def create_vehicle(
    info: schemas.VehicleInfoCreate,
    db: Session = Depends(get_db)
):
    """
    将前端传来的 VehicleInfoCreate 数据保存到数据库，
    若重复则给出友好提示。
    """
    # —— 1. 重复检测 ——
    if info.license != "无":
        dup = db.query(models.VehicleInfo)\
                .filter(models.VehicleInfo.license == info.license)\
                .first()
    else:
        dup = db.query(models.VehicleInfo).filter(
            models.VehicleInfo.license == "无",
            models.VehicleInfo.Brand == info.Brand,
            models.VehicleInfo.color == info.color,
            models.VehicleInfo.original_location == info.original_location,
            models.VehicleInfo.current_location == info.current_location,
            models.VehicleInfo.attachment == info.attachment,
            models.VehicleInfo.other_feature == info.other_feature,
        ).first()

    if dup:
        # 已登记过
        return JSONResponse(status_code=200, content={"message": "您输入的数据已经登记"})

    # —— 2. 否则正常写库并返回 ——
    try:
        new_obj = crud.create_vehicle_info(db, info)
        return new_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# GET 路由：按条件查询车辆信息
@app.get(
    "/vehicle/info",
    response_model=schemas.VehicleInfoList,
    dependencies=[Depends(verify_api_key)]
)
def get_vehicle(
    original_location: str,
    color: str,
    license: str = None,
    Brand: str = None,
    attachment: str = None,
    other_feature: str = None,
    db: Session = Depends(get_db)
):
    """
    按条件查询 VehicleInfo 数据，返回包装在 VehicleInfoList schema 中的结果列表。
    """
    res = crud.query_vehicle_info(
        db,
        original_location=original_location,
        color=color,
        license=license,
        Brand=Brand,
        attachment=attachment,
        other_feature=other_feature,
    )
    if not res:
        # 没有查到时返回友好提示
        return JSONResponse(status_code=200, content={"message": "数据不存在"})

    return schemas.VehicleInfoList(items=res)
