import sqlalchemy
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError

# Создание объекта FastAPI
app = FastAPI()

# Настройка базы данных MySQL
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://isp_p_Podushko:12345@192.168.25.23/isp_p_Podushko"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Определение модели SQLAlchemy для пользователя
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True)  # Указываем длину для VARCHAR
    email = Column(String(100), unique=True, index=True)  # Указываем длину для VARCHAR

class Contracts(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(String(30), index=True)
    workshop_head = Column(String(50), index=True)
    phone = Column(String(11), index=True)

class Goods(Base):
    __tablename__ = "goods"

    id = Column(Integer, primary_key=True, index=True)
    good_name = Column(String(50), index=True)
    workshop_id = Column(Integer, index=True)
    unit_cost = Column(Integer, index=True)

class Orders(Base):
    __tablename__ = "orders"

    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False, index=True, primary_key=True)
    good_id = Column(Integer, ForeignKey("goods.id"), index=True)
    amount = Column(Integer, index=True)

class Workshop(Base):
    __tablename__ = "workshops"
    id = Column(Integer, nullable=False, index=True, primary_key=True)
    name = Column(String(30), index=True)
    workshop_head = Column(String(50), index=True)
    phone = Column(String(11), index=True)

# Создание таблиц в базе данных (закоментирована чтобы не пересоздавать таблицы каждый раз)
# Base.metadata.create_all(bind=engine)

# Определение Pydantic модели для пользователя
class UserCreate(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        orm_mode = True

class GoodsCreate(BaseModel):
    good_name: str
    workshop_id: int
    unit_cost: int

class GoodsResponse(BaseModel):
    id: int
    good_name: str
    workshop_id: int
    unit_cost: int

    class Config:
        orm_mode = True

class WorkshopCreate(BaseModel):
    name: str
    workshop_head: str
    phone: str

class WorkshopResponse(BaseModel):
    id: int
    name: str
    workshop_head: str
    phone: str

    class Config:
        orm_mode = True

# Зависимость для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Маршрут для получения пользователя по ID
@app.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Маршрут для создания нового пользователя
@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(name=user.name, email=user.email)
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")

# Маршрут для получения товара по ID
@app.get("/goods/{good_id}", response_model=GoodsResponse)
def read_good(good_id: int, db: Session = Depends(get_db)):
    good = db.query(Goods).filter(Goods.id == good_id).first()
    if good is None:
        raise HTTPException(status_code=404, detail="Good not found")
    return good

# Маршрут для создания нового товара
@app.post("/goods/", response_model=GoodsResponse)
def create_good(good: GoodsCreate, db: Session = Depends(get_db)):
    db_good = Goods(good_name=good.good_name, workshop_id=good.workshop_id, unit_cost=good.unit_cost)
    try:
        db.add(db_good)
        db.commit()
        db.refresh(db_good)
        return db_good
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Good is already existed")

@app.delete("/goods/{good_id}", response_model=GoodsResponse)
def delete_good(good_id: int, db: Session = Depends(get_db)):
    good = db.query(Goods).filter(Goods.id == good_id).first()
    if good is None:
        raise HTTPException(status_code=404, detail="Good not found")
    else:
        db.delete(good)
        db.commit()
        return good
