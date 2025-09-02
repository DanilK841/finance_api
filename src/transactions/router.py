from datetime import datetime
from http.client import HTTPException

from fastapi import APIRouter, Depends
from sqlalchemy import update
from sqlalchemy.orm import Session, joinedload

from src.classes import TransactionTypesResponse, TransactionTypesCreate, TransactionTypesUpdate, TransactionResponse, \
    TransactionCreate, UserTransactions, TransactionUpdate
from src.database import get_db, Transactions, TransactionTypes, Users

router = APIRouter(prefix='transaction', tags=['ТРАНЗАКЦИИ'])

@router.post("/trans/", response_model=TransactionResponse)
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

@router.get("/user_transactions/{user_id}", response_model=UserTransactions)
def get_user_trans(user_id: int, session: Session = Depends(get_db)):
    db_user = session.query(Users).options(joinedload(Users.transactions)).filter(Users.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/transactions/{trans_id}", response_model=TransactionResponse)
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

@router.delete("/transactions/{trans_id}")
def delete_trans(trans_id: int, session: Session = Depends(get_db)):
    db_trans = session.query(Transactions).filter(Transactions.id == trans_id).first()
    # db_trans = Transactions.query.get_or_404(trans_id)
    session.delete(db_trans)
    session.commit()
    return {"msg":f"Delete transaction with id {trans_id} succes"}