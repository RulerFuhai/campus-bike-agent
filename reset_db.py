# reset_db.py
from app.database import engine
from app.models import Base

if __name__ == "__main__":
    # 删除旧表
    Base.metadata.drop_all(bind=engine)
    # 按最新模型建表
    Base.metadata.create_all(bind=engine)
    print("✅ 已删除并重建所有表")
