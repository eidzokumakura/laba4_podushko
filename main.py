import sqlalchemy
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError

# Создание объекта FastAPI
app = FastAPI()

# Настройка базы данных MySQL
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://isp_p_Podushko:12345@77.91.86.135/isp_p_Podushko"
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
    address = Column(String(50), index=True)
    date_registration = Column(Date, index=True, nullable=False)
    date_completion = Column(Date, index=True)

class Goods(Base):
    __tablename__ = "goods"

    id = Column(Integer, primary_key=True, index=True)
    good_name = Column(String(50), index=True)
    workshop_id = Column(Integer, ForeignKey("workshops.id"), index=True)
    unit_cost = Column(Integer, index=True)

class Orders(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False, index=True, primary_key=True)
    good_id = Column(Integer, ForeignKey("goods.id"), index=True)
    amount = Column(Integer, index=True)

class Workshops(Base):
    __tablename__ = "workshops"
    id = Column(Integer, nullable=False, index=True, primary_key=True)
    name = Column(String(30), index=True)
    workshop_head = Column(String(50), index=True)
    phone = Column(String(11), index=True)

# Создание таблиц в базе данных (закоментирована чтобы не пересоздавать таблицы каждый раз)
Base.metadata.create_all(bind=engine)

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

class ContractsCreate(BaseModel):
    name: str
    address: str
    date_registration: str
    date_completion: str

class ContractsResponse(BaseModel):
    id: int
    name: str
    address: str
    date_registration: str
    date_completion: str
    class Config:
        orm_mode = True
class OrdersCreate(BaseModel):
    contract_id: int
    good_id: int
    amount: int

class OrdersResponse(BaseModel):
    id: int
    contract_id: int
    good_id: int
    amount: int
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

# GOODS
@app.get("/goods/{good_id}", response_model=GoodsResponse)
def read_good(good_id: int, db: Session = Depends(get_db)):
    good = db.query(Goods).filter(Goods.id == good_id).first()
    if good is None:
        raise HTTPException(status_code=404, detail="Good not found")
    return good

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

@app.put("/goods/{good_id}", response_model=GoodsResponse)
def update_good(good_id: int, good: GoodsCreate, db: Session = Depends(get_db)):
    db_good = Goods(good_name=good.good_name, workshop_id=good.workshop_id, unit_cost=good.unit_cost)
    current_good = db.query(Goods).filter(Goods.id == good_id).first()
    if current_good is None:
        raise HTTPException(status_code=404, detail="Good not found")
    else:
        current_good.good_name = db_good.good_name
        current_good.workshop_id = db_good.workshop_id
        current_good.unit_cost = db_good.unit_cost
        db.add(current_good)
        db.commit()
        db.refresh(current_good)
    return current_good

# WORKSHOP
@app.get("/workshops/{workshop_id}", response_model=WorkshopResponse)
def read_workshop(workshop_id: int, db: Session = Depends(get_db)):
    workshop = db.query(Workshops).filter(Workshops.id == workshop_id).first()
    if workshop is None:
        raise HTTPException(status_code=404, detail="Workshop not found")
    return workshop

@app.post("/workshops/", response_model=WorkshopResponse)
def create_workshop(workshop: WorkshopCreate, db: Session = Depends(get_db)):
    db_workshop = Workshops(name=workshop.name, workshop_head=workshop.workshop_head, phone=workshop.phone)
    try:
        db.add(db_workshop)
        db.commit()
        db.refresh(db_workshop)
        return db_workshop
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Workshop is already existed")

@app.delete("/workshops/{workshop_id}", response_model=WorkshopResponse)
def delete_workshop(workshop_id: int, db: Session = Depends(get_db)):
    workshop = db.query(Workshops).filter(Workshops.id == workshop_id).first()
    if workshop is None:
        raise HTTPException(status_code=404, detail="Workshop not found")
    else:
        db.delete(workshop)
        db.commit()
        return workshop

@app.put("/workshop/{workshop_id}", response_model=WorkshopResponse)
def update_workshop(workshop_id: int, workshop: WorkshopCreate, db: Session = Depends(get_db)):
    db_workshop = Workshops(name=workshop.name, workshop_head=workshop.workshop_head, phone=workshop.phone)
    current_workshop = db.query(Workshops).filter(Workshops.id == workshop_id).first()
    if current_workshop is None:
        raise HTTPException(status_code=404, detail="Workshop not found")
    else:
        current_workshop.name = db_workshop.name
        current_workshop.workshop_head = db_workshop.workshop_head
        current_workshop.phone = db_workshop.phone
        db.add(current_workshop)
        db.commit()
        db.refresh(current_workshop)
    return current_workshop

# ORDERS
@app.get("/orders/{order_id}", response_model=OrdersResponse)
def read_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Orders).filter(Orders.id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.post("/orders/", response_model=OrdersResponse)
def create_order(order: OrdersCreate, db: Session = Depends(get_db)):
    db_order = Orders(contract_id=order.contract_id, good_id=order.good_id, amount=order.amount)
    try:
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        return db_order
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Order is already existed")

@app.delete("/orders/{order_id}", response_model=OrdersResponse)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Orders).filter(Orders.id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Workshop not found")
    else:
        db.delete(order)
        db.commit()
        return order

@app.put("/orders/{order_id}", response_model=OrdersResponse)
def update_order(order_id: int, order: OrdersCreate, db: Session = Depends(get_db)):
    db_order = Orders(contract_id=order.contract_id, good_id=order.good_id, amount=order.amount)
    current_order = db.query(Orders).filter(Orders.id == order_id).first()
    if current_order is None:
        raise HTTPException(status_code=404, detail="Workshop not found")
    else:
        current_order.contract_id = db_order.contract_id
        current_order.good_id= db_order.good_id
        current_order.amount = db_order.amount
        db.add(current_order)
        db.commit()
        db.refresh(current_order)
    return current_order

# CONTRACTS
@app.get("/contracts/{contract_id}", response_model=ContractsResponse)
def read_contract(contract_id: int, db: Session = Depends(get_db)):
    contract = db.query(Contracts).filter(Contracts.id == contract_id).first()
    if contract is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return contract

@app.post("/contracts/", response_model=ContractsResponse)
def create_contract(contract: ContractsCreate, db: Session = Depends(get_db)):
    db_contract = Contracts(name=contract.name, date_registration=contract.date_registration, date_completion=contract.date_completion)
    try:
        db.add(db_contract)
        db.commit()
        db.refresh(db_contract)
        return db_contract
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Contract is already existed")

@app.delete("/contracts/{contract_id}", response_model=ContractsResponse)
def delete_contract(contract_id: int, db: Session = Depends(get_db)):
    contract = db.query(Contracts).filter(Contracts.id == contract_id).first()
    if contract is None:
        raise HTTPException(status_code=404, detail="Workshop not found")
    else:
        db.delete(contract)
        db.commit()
        return contract

@app.put("/contracts/{contract_id}", response_model=ContractsResponse)
def update_contract(contract_id: int, contract: ContractsCreate, db: Session = Depends(get_db)):
    db_contract = Contracts(name=contract.name, date_registration=contract.date_registration, date_completion=contract.date_completion)
    current_contract = db.query(Contracts).filter(Contracts.id == contract_id).first()
    if current_contract is None:
        raise HTTPException(status_code=404, detail="Workshop not found")
    else:
        current_contract.name = db_contract.name
        current_contract.date_registration = db_contract.date_registration
        current_contract.date_completion = db_contract.date_completion
        db.add(current_contract)
        db.commit()
        db.refresh(current_contract)
    return current_contract