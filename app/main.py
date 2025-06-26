# app/main.py
from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List
import os
from dotenv import load_dotenv

from . import crud, models, schemas
from .database import SessionLocal, engine

load_dotenv()
API_KEY = os.getenv("PLUGIN_API_KEY")

models.Base.metadata.create_all(bind=engine)
app = FastAPI(title="Vehicle Info Plugin")

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

@app.get(
    "/vehicle/info",
    response_model=List[schemas.VehicleInfoOut],
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
        raise HTTPException(status_code=404, detail="No records found")
    return res
