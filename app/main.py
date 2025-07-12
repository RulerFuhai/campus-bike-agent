import socket
# —— Monkey-patch：让 Python 只返回 IPv4 地址 ——
_orig_getaddrinfo = socket.getaddrinfo
def _getaddrinfo_ipv4(host, port, family=0, type=0, proto=0, flags=0):
    infos = _orig_getaddrinfo(host, port, family, type, proto, flags)
    # 只保留 IPv4 (AF_INET) 条目
    return [info for info in infos if info[0] == socket.AF_INET]
socket.getaddrinfo = _getaddrinfo_ipv4

import os
import smtplib
import traceback
from typing import List
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from email.mime.text import MIMEText
from email.header import Header as EmailHeader
from dotenv import load_dotenv

from app import crud, models, schemas
from app.database import SessionLocal, engine

# ——— 环境 & 数据库 初始化 ———
load_dotenv()
API_KEY = os.getenv("PLUGIN_API_KEY")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

# SMTP 邮件配置
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
MAIL_SENDER = os.getenv("MAIL_SENDER")

# 自动创建表
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Vehicle Info Plugin")


# —— 依赖：数据库会话 ——
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# —— 依赖：插件 API Key 验证 ——
def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")


# —— 依赖：超级管理员密码验证 ——
def verify_admin_password(x_admin_password: str = Header(..., alias="X-Admin-Password")):
    if x_admin_password != ADMIN_PASSWORD:
        return JSONResponse(status_code=200, content={"message": "密码错误，拒绝访问"})


# — POST /vehicle/info — 登记车辆 ——
@app.post(
    "/vehicle/info",
    response_model=schemas.VehicleInfoOut,
    dependencies=[Depends(verify_api_key)]
)
def create_vehicle(
    info: schemas.VehicleInfoCreate,
    db: Session = Depends(get_db)
):
    # —— 重复检测 ——
    if info.license != "无":
        dup = db.query(models.VehicleInfo).filter(
            models.VehicleInfo.license == info.license
        ).first()
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
        return JSONResponse(status_code=200, content={"message": "您输入的数据已经登记"})

    try:
        new_obj = crud.create_vehicle_info(db, info)
        return new_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# — GET /vehicle/info — 查询车辆 ——
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
        return JSONResponse(status_code=200, content={"message": "数据不存在"})
    return schemas.VehicleInfoList(items=res)


# — POST /admin/login — 超管登录 ——
@app.post(
    "/admin/login",
    response_model=schemas.AdminLoginResponse
)
def admin_login(req: schemas.AdminLoginRequest):
    if req.password != ADMIN_PASSWORD:
        return JSONResponse(status_code=200, content={"message": "密码错误，拒绝访问"})
    menu = ["browse_data", "delete_data", "clear_data"]
    return schemas.AdminLoginResponse(message="登录成功", menu=menu)


# — GET /admin/vehicles — 浏览所有数据 ——
@app.get(
    "/admin/vehicles",
    response_model=schemas.VehicleInfoList,
    dependencies=[Depends(verify_admin_password)]
)
def admin_get_all(db: Session = Depends(get_db)):
    all_items = crud.get_all_vehicles(db)
    return schemas.VehicleInfoList(items=all_items)


# — DELETE /admin/vehicle/{vehicle_id} — 删除指定记录 ——
@app.delete(
    "/admin/vehicle/{vehicle_id}",
    response_model=schemas.Message,
    dependencies=[Depends(verify_admin_password)]
)
def admin_delete_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_vehicle_by_id(db, vehicle_id)
    if not ok:
        return JSONResponse(status_code=200, content={"message": "数据不存在"})
    return schemas.Message(message=f"已删除车辆ID: {vehicle_id}")


# — DELETE /admin/vehicles — 清空所有数据 ——
@app.delete(
    "/admin/vehicles",
    response_model=schemas.Message,
    dependencies=[Depends(verify_admin_password)]
)
def admin_clear_vehicles(db: Session = Depends(get_db)):
    count = crud.clear_all_vehicles(db)
    return schemas.Message(message=f"已清空全部车辆数据，共删除 {count} 条记录")


# — POST /binding — 车主邮箱绑定 ——
@app.post(
    "/binding",
    response_model=schemas.LicenseBindingOut,
    dependencies=[Depends(verify_api_key)]
)
def bind_license(info: schemas.LicenseBindingCreate, db: Session = Depends(get_db)):
    obj = crud.bind_license_email(db, info)
    return obj


# — GET /binding — 查询绑定 ——
@app.get(
    "/binding",
    dependencies=[Depends(verify_api_key)]
)
def query_binding(license: str, db: Session = Depends(get_db)):
    bind = crud.get_binding(db, license)
    if not bind:
        return JSONResponse(status_code=200, content={"message": "未绑定"})
    return schemas.LicenseBindingOut.from_orm(bind)


# — GET /alert — 违停通知 ——
@app.get(
    "/alert",
    dependencies=[Depends(verify_api_key)]
)
def parking_alert(license: str, db: Session = Depends(get_db)):
    bind = crud.get_binding(db, license)
    if not bind:
        return JSONResponse(status_code=200, content={"message": "未绑定，无法通知"})

    subject = "违停通知"
    body = f"您的车辆（车牌 {license}）在校园内违停，请尽快来移车。"
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = EmailHeader(subject, "utf-8")
    msg["From"] = MAIL_SENDER
    msg["To"] = bind.email

    try:
        # 使用 SSL 直连 465
        server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=30)
        print("SMTP_SSL: connect OK", flush=True)
        server.login(SMTP_USER, SMTP_PASSWORD)
        print("SMTP_SSL: login OK", flush=True)
        server.sendmail(MAIL_SENDER, [bind.email], msg.as_string())
        print("SMTP_SSL: sendmail OK", flush=True)
        server.quit()
    except Exception:
        tb = traceback.format_exc()
        print(tb, flush=True)
        raise HTTPException(status_code=500, detail=tb)

    return JSONResponse(status_code=200, content={"message": f"已通知 {bind.email}"})
