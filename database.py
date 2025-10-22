from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# 1. إعداد الاتصال
DATABASE_URL = "sqlite:///./masterpiece_inventory.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. تعريف جدول المنتج بالتفاصيل الدقيقة الجديدة
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True) # اسم المنتج فريد
    description = Column(String, default="") # الوصف
    category = Column(String, default="") # الفئة أو المجموعة
    supplier = Column(String, default="") # المورّد
    quantity = Column(Integer, default=0) # الكمية
    price = Column(Integer, default=0) # السعر (رقم صحيح)
    reorder_level = Column(Integer, default=5) # حد إعادة الطلب (للتنبيهات)
    added_at = Column(DateTime, default=datetime.utcnow) # زمن الإضافة

# 3. إنشاء الجداول في قاعدة البيانات
def create_db():
    Base.metadata.create_all(bind=engine)
