from fastapi import FastAPI, Depends, HTTPException

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, update, delete
from database import *
from classes import *


app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post("/user/", response_model=UserResponse)
# как правильно описать процесс который тут вызван
# session: Session = Depends(get_db)
def create_user(user: UserCreate, session: Session = Depends(get_db)):
    db_user = Users(
        name=user.name,
        password=user.password
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@app.put("/user_update/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserUpdate, session: Session = Depends(get_db)):

    user_db = session.query(Users).filter(Users.id == user_id).first()
    name = user.name if user.name else user_db.name
    password = user.password if user.password else user_db.password

    update_stmt = update(Users).where(Users.id == user_id).values(
            name= name,
            password= password,
            updated_at= datetime.utcnow()
    )
    session.execute(update_stmt)
    session.commit()
    session.refresh(user_db)
    return user_db

@app.get("/user/{user_id}", response_model=UserResponse)
def update_user(user_id: int, session: Session = Depends(get_db)):
    user_db = session.query(Users).filter(Users.id == user_id).first()
    return user_db

@app.get("/users/", response_model=list[UserResponse])
def update_user(session: Session = Depends(get_db)):
    user_db = session.query(Users).all()
    return user_db


@app.post("/trans_type/", response_model=TransactionTypesResponse)
def create_tr_types(trtypes: TransactionTypesCreate, session: Session = Depends(get_db)):
    db_trtypes = TransactionTypes(
        name=trtypes.name,
        description=trtypes.description
    )
    session.add(db_trtypes)
    session.commit()
    session.refresh(db_trtypes)
    return db_trtypes

@app.put("/trans_type/{update_id}", response_model=TransactionTypesResponse)
def update_tr_types(update_id: int, trtypes: TransactionTypesUpdate, session: Session = Depends(get_db)):
    db_trtypes = session.query(TransactionTypes).filter(TransactionTypes.id == update_id).first()
    name = trtypes.name if trtypes.name else db_trtypes.name
    description = trtypes.description if trtypes.description else db_trtypes.description

    updt_stmt = update(TransactionTypes).where(TransactionTypes.id == update_id).values(
        name=name,
        description=description
    )
    session.execute(updt_stmt)
    session.commit()
    session.refresh(db_trtypes)
    return db_trtypes

@app.get("/trans_types/", response_model=list[TransactionTypesResponse])
def get_all_types(session: Session = Depends(get_db)):
    db_trtypes = session.query(TransactionTypes).all()
    return db_trtypes

@app.get("/trans_type/{id}", response_model=TransactionTypesResponse)
def get_all_types(id: int, session: Session = Depends(get_db)):
    db_trtypes = session.query(TransactionTypes).filter(TransactionTypes.id == id).first()
    return db_trtypes


@app.post("/trans/", response_model=TransactionResponse)
def create_transaction(trans: TransactionCreate, session: Session = Depends(get_db)):
    user = session.query(Users).filter(Users.id == trans.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    trans_type = session.query(TransactionTypes).filter(TransactionTypes.id == trans.type_id).first()
    if not trans_type:
        raise HTTPException(status_code=404, detail="Type transactions not found")

    db_trans = Transactions(**trans.dict())
    session.add(db_trans)
    session.commit()
    session.refresh(db_trans)
    return db_trans

@app.get("/user_transactions/{user_id}", response_model=UserTransactions)
def get_user_trans(user_id: int, session: Session = Depends(get_db)):
    db_user = session.query(Users).options(joinedload(Users.transactions)).filter(Users.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.put("/transactions/{trans_id}", response_model=TransactionResponse)
def get_user_trans(trans_id: int, trans: TransactionUpdate, session: Session = Depends(get_db)):
    db_trans = session.query(Transactions).filter(Transactions.id == trans_id).first()
    amount = trans.amount if trans.amount else db_trans.amount
    if amount < 0:
        raise HTTPException(status_code=404, detail="Amount must be greater than 0")
    category = trans.category if trans.category else db_trans.category
    status = trans.status if trans.status else db_trans.status
    type_id = trans.type_id if trans.type_id else db_trans.type_id
    trans_type = session.query(TransactionTypes).filter(TransactionTypes.id == type_id).first()
    if not trans_type:
        raise HTTPException(status_code=404, detail="Type transactions not found")


    update_stmt = update(Transactions).where(Transactions.id == trans_id).values(
        amount=amount,
        category=category,
        status=status,
        type_id=type_id
    )
    session.execute(update_stmt)
    session.commit()
    session.refresh(db_trans)
    return db_trans

@app.delete("/transactions/{trans_id}")
def delete_trans(trans_id: int, session: Session = Depends(get_db)):
    db_trans = session.query(Transactions).filter(Transactions.id == trans_id).first()
    # db_trans = Transactions.query.get_or_404(trans_id)
    session.delete(db_trans)
    session.commit()
    return {"msg":f"Delete transaction with id {trans_id} succes"}

@app.delete("/user/{user_id}")
def delete_trans(user_id: int, session: Session = Depends(get_db)):
    db_trans = session.query(Transactions).filter(Transactions.user_id == user_id)
    if db_trans:
        HTTPException(status_code=404, detail="Exist transactions with this user")

    db_user = session.query(Users).filter(Users.id == user_id).first()
    session.delete(db_user)
    session.commit()
    return {"msg":f"Delete user with name {db_user.name} succes"}


@app.delete("/trans_type/{trans_t_id}")
def delete_trans(trans_t_id: int, session: Session = Depends(get_db)):
    db_trans = session.query(Transactions).filter(Transactions.type_id == trans_t_id)
    if db_trans:
        HTTPException(status_code=404, detail="Exist transactions with this transaction_types")

    db_trans_type = session.query(TransactionTypes).filter(TransactionTypes.id == trans_t_id).first()
    session.delete(db_trans_type)
    session.commit()
    return {"msg": f"Delete transaction type with name {db_trans_type.name} succes"}