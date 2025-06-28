# app/main.py
import os
from typing import List

from fastapi import FastAPI, Depends, HTTPException, Header
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
    将前端传来的 VehicleInfoCreate 数据保存到数据库，返回保存后的完整 VehicleInfoOut 对象（包含 id 字段）。
    """
    return crud.create_vehicle_info(db, info)


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
    必填 original_location、color，可选 license、Brand、attachment、other_feature。
    返回所有匹配的 VehicleInfo 记录列表，包装在 items 字段中。
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
        raise HTTPException(status_code=404, detail="No records found")

    # 返回包装在 'items' 字段中的列表
    return schemas.VehicleInfoList(items=res)
